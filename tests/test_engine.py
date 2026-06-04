from datetime import datetime, timezone
from decimal import Decimal

import pytest

# We are importing a function from the engine that does not exist yet.
from src.engine import calculate_net_balances

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
