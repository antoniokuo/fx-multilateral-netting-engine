from datetime import datetime, timezone
from decimal import Decimal

import pytest

# We are importing the Transaction class that we haven't written yet!
from src.models import Transaction


def test_transaction_instantiates_with_valid_data():
    """
    Test that a Transaction object can be created with strict types.
    """
    # 1. Arrange & Act: We try to create the object
    tx = Transaction(
        id="tx-12345",
        timestamp=datetime.now(timezone.utc),
        debtor="Alice",
        creditor="Bob",
        currency="GBP",
        amount=Decimal("50.00"),
    )

    # 2. Assert: We verify the data is stored exactly as passed
    assert tx.debtor == "Alice"
    assert tx.creditor == "Bob"
    assert tx.amount == Decimal("50.00")
    assert tx.currency == "GBP"
