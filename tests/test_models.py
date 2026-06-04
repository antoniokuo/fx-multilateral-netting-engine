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


def test_transaction_rejects_zero_or_negative_amount():
    """
    Test that the system violently rejects non-positive financial amounts.
    """
    with pytest.raises(ValueError, match="Amount must be strictly positive"):
        Transaction(
            id="tx-error-1",
            timestamp=datetime.now(timezone.utc),
            debtor="Alice",
            creditor="Bob",
            currency="GBP",
            amount=Decimal("-50.00"),
        )


def test_transaction_rejects_self_debt():
    """
    Test that a node cannot have a directed edge to itself.
    """
    with pytest.raises(
        ValueError, match="Debtor and creditor cannot be the same entity"
    ):
        Transaction(
            id="tx-error-2",
            timestamp=datetime.now(timezone.utc),
            debtor="Alice",
            creditor="Alice",
            currency="GBP",
            amount=Decimal("50.00"),
        )
