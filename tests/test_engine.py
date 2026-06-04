from datetime import datetime, timezone
from decimal import Decimal

import pytest

# We are importing a function from the engine that does not exist yet.
from src.engine import calculate_net_balances, route_settlement
from src.models import Transaction


def test_calculate_net_balances_resolves_complex_graph():
    """
    Test that the engine accurately aggregates a sequence of directed edges
    into a zero-sum net balance dictionary.
    """
    # 1. Arrange: Create a web of transactions
    tx1 = Transaction(
        id="tx-1",
        timestamp=datetime.now(timezone.utc),
        debtor="Alice",
        creditor="Bob",
        currency="GBP",
        amount=Decimal("50.00"),
    )
    tx2 = Transaction(
        id="tx-2",
        timestamp=datetime.now(timezone.utc),
        debtor="Charlie",
        creditor="Alice",
        currency="GBP",
        amount=Decimal("20.00"),
    )
    tx3 = Transaction(
        id="tx-3",
        timestamp=datetime.now(timezone.utc),
        debtor="Bob",
        creditor="Charlie",
        currency="GBP",
        amount=Decimal("10.00"),
    )

    ledger = [tx1, tx2, tx3]

    # 2. Act: Calculate the absolute state
    balances = calculate_net_balances(ledger)

    # 3. Assert: Verify the exact mathematical state
    # Alice: -50 (tx1) + 20 (tx2) = -30
    # Bob: +50 (tx1) - 10 (tx3) = +40
    # Charlie: -20 (tx2) + 10 (tx3) = -10
    assert balances["Alice"] == Decimal("-30.00")
    assert balances["Bob"] == Decimal("40.00")
    assert balances["Charlie"] == Decimal("-10.00")

    # Mathematical property constraint: The system must be perfectly zero-sum
    assert sum(balances.values()) == Decimal("0.00")


def test_route_settlement_transactions():
    """
    Test that the engine resolves a net balance dictionary into the absolute
    minimum number of settlement transactions.
    """
    # 1. Arrange: The absolute state of the network
    balances = {
        "Alice": Decimal("-30.00"),
        "Bob": Decimal("40.00"),
        "Charlie": Decimal("-10.00"),
    }

    # 2. Act: Execute the minimum cash flow routing
    # We pass "GBP" to enforce the currency of the output transactions
    settlements = route_settlement(balances, currency="GBP")

    # 3. Assert: Mathematical verification
    # For 3 entities, the maximum number of optimal transactions is V - 1 = 2
    assert len(settlements) <= 2

    # We prove the algorithm worked by passing its output back into our first function.
    # The net balances of the settlement transactions MUST perfectly match the initial debt.
    net_settled = calculate_net_balances(settlements)

    assert net_settled["Alice"] == Decimal("-30.00")
    assert net_settled["Bob"] == Decimal("40.00")
    assert net_settled["Charlie"] == Decimal("-10.00")
