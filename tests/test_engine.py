import uuid
from datetime import datetime, timezone
from decimal import Decimal

from src.engine import (
    calculate_global_net_balances,
    calculate_net_balances,
    route_settlement,
)
from src.fx import StaticFXProvider
from src.models import Transaction


def test_calculate_net_balances_resolves_complex_graph() -> None:
    """
    Test that the engine accurately aggregates a sequence of directed edges
    into a zero-sum net balance dictionary.
    """
    tx1 = Transaction(
        id=str(uuid.uuid4()),
        timestamp=datetime.now(timezone.utc),
        debtor="Alice",
        creditor="Bob",
        currency="GBP",
        amount=Decimal("50.00"),
    )
    tx2 = Transaction(
        id=str(uuid.uuid4()),
        timestamp=datetime.now(timezone.utc),
        debtor="Charlie",
        creditor="Alice",
        currency="GBP",
        amount=Decimal("20.00"),
    )
    tx3 = Transaction(
        id=str(uuid.uuid4()),
        timestamp=datetime.now(timezone.utc),
        debtor="Bob",
        creditor="Charlie",
        currency="GBP",
        amount=Decimal("10.00"),
    )

    ledger = [tx1, tx2, tx3]
    balances = calculate_net_balances(ledger)

    # Assertions expect the nested currency key
    assert balances["GBP"]["Alice"] == Decimal("-30.00")
    assert balances["GBP"]["Bob"] == Decimal("40.00")
    assert balances["GBP"]["Charlie"] == Decimal("-10.00")
    assert sum(balances["GBP"].values()) == Decimal("0.00")


def test_calculate_net_balances_isolates_multiple_currencies() -> None:
    """
    Test that the engine strictly partitions balances by currency,
    preventing catastrophic cross-currency arithmetic.
    """
    tx1 = Transaction(
        id=str(uuid.uuid4()),
        timestamp=datetime.now(timezone.utc),
        debtor="Alice",
        creditor="Bob",
        currency="GBP",
        amount=Decimal("50.00"),
    )
    tx2 = Transaction(
        id=str(uuid.uuid4()),
        timestamp=datetime.now(timezone.utc),
        debtor="Bob",
        creditor="Alice",
        currency="EUR",
        amount=Decimal("40.00"),
    )

    ledger = [tx1, tx2]
    balances = calculate_net_balances(ledger)

    # GBP Graph
    assert balances["GBP"]["Alice"] == Decimal("-50.00")
    assert balances["GBP"]["Bob"] == Decimal("50.00")
    assert sum(balances["GBP"].values()) == Decimal("0.00")

    # EUR Graph
    assert balances["EUR"]["Bob"] == Decimal("-40.00")
    assert balances["EUR"]["Alice"] == Decimal("40.00")
    assert sum(balances["EUR"].values()) == Decimal("0.00")


def test_route_settlement_transactions() -> None:
    """
    Test that the engine resolves a net balance dictionary into the absolute
    minimum number of settlement transactions.
    """
    # The routing engine still accepts a flat dictionary for a SINGLE currency
    single_currency_balances = {
        "Alice": Decimal("-30.00"),
        "Bob": Decimal("40.00"),
        "Charlie": Decimal("-10.00"),
    }

    settlements = route_settlement(single_currency_balances, currency="GBP")

    assert len(settlements) <= 2

    # Recalculating the net of the settlements will yield a nested dictionary
    net_settled = calculate_net_balances(settlements)

    assert net_settled["GBP"]["Alice"] == Decimal("-30.00")
    assert net_settled["GBP"]["Bob"] == Decimal("40.00")
    assert net_settled["GBP"]["Charlie"] == Decimal("-10.00")


def test_calculate_net_balances_handles_empty_ledger() -> None:
    """
    Test that an empty ledger safely returns an empty dictionary, not an error.
    """
    balances = calculate_net_balances([])
    assert balances == {}


def test_calculate_net_balances_handles_asymmetrical_graph() -> None:
    """
    Test a one-way debt graph where capital flows out but not in.
    """
    tx1 = Transaction(
        id=str(uuid.uuid4()),
        timestamp=datetime.now(timezone.utc),
        debtor="Alice",
        creditor="Bob",
        currency="GBP",
        amount=Decimal("50.00"),
    )

    balances = calculate_net_balances([tx1])

    assert balances["GBP"]["Alice"] == Decimal("-50.00")
    assert balances["GBP"]["Bob"] == Decimal("50.00")
    assert sum(balances["GBP"].values()) == Decimal("0.00")


def test_calculate_global_net_balances_cross_currency() -> None:
    """
    Test that the engine mathematically collapses a multi-currency partitioned graph
    into a zero-sum, single base-currency ledger using an injected FX Strategy.
    """
    # 1. Arrange: The partitioned multi-currency state
    partitioned_balances = {
        "GBP": {"Alice": Decimal("-100.00"), "Bob": Decimal("100.00")},
        "EUR": {"Alice": Decimal("125.00"), "Bob": Decimal("-125.00")},
    }

    # 2. Arrange: The Deterministic FX Strategy
    # We enforce exact ratios to avoid rounding drift during the test
    rates = {
        ("EUR", "GBP"): Decimal("0.80"),  # €1.00 = £0.80
        ("GBP", "EUR"): Decimal("1.25"),  # £1.00 = €1.25
    }
    provider = StaticFXProvider(rates)

    # 3. Act: Collapse the graph into a GBP base currency
    global_balances = calculate_global_net_balances(
        partitioned_balances, provider, base_currency="GBP"
    )

    # 4. Assert: Mathematical Verification
    # Alice owes £100 but is owed €125.
    # €125 * 0.80 = £100.
    # Alice's debt and credit perfectly annihilate each other.
    assert global_balances["Alice"] == Decimal("0.00")
    assert global_balances["Bob"] == Decimal("0.00")
