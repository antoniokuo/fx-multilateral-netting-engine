from datetime import datetime, timezone
from decimal import Decimal

import pytest

# We are importing the Transaction class that we haven't written yet!
from src.models import Transaction


def test_transaction_instantiates_with_valid_data() -> None:
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


def test_transaction_rejects_zero_or_negative_amount() -> None:
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


def test_transaction_rejects_self_debt() -> None:
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


def test_transaction_rejects_invalid_currency_format() -> None:
    """
    Test that the system enforces strict 3-letter uppercase ISO 4217 currency codes.
    """
    invalid_currencies = ["gbp", "US DOLLAR", "EUR ", "123", "UK"]

    for bad_currency in invalid_currencies:
        with pytest.raises(
            ValueError, match="Currency must be a 3-letter uppercase string"
        ):
            Transaction(
                id="tx-error-3",
                timestamp=datetime.now(timezone.utc),
                debtor="Alice",
                creditor="Bob",
                currency=bad_currency,
                amount=Decimal("50.00"),
            )


def test_transaction_rejects_naive_datetime() -> None:
    """
    Test that the system violently rejects naive datetimes lacking timezone data.
    """
    # Generate a naive datetime (no timezone attached)
    naive_dt = datetime.now()

    with pytest.raises(ValueError, match="Timestamp must be timezone-aware"):
        Transaction(
            id="tx-error-4",
            timestamp=naive_dt,
            debtor="Alice",
            creditor="Bob",
            currency="GBP",
            amount=Decimal("50.00"),
        )
