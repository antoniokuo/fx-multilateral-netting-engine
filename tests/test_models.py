import uuid
from datetime import datetime, timezone
from decimal import Decimal

import pytest

from src.models import Transaction


def test_transaction_instantiates_with_valid_data() -> None:
    tx = Transaction(
        id=str(uuid.uuid4()),
        timestamp=datetime.now(timezone.utc),
        debtor="Alice",
        creditor="Bob",
        currency="GBP",
        amount=Decimal("50.00"),
    )
    assert tx.debtor == "Alice"
    assert tx.amount == Decimal("50.00")


def test_transaction_rejects_zero_or_negative_amount() -> None:
    with pytest.raises(ValueError, match="Amount must be strictly positive"):
        Transaction(
            id=str(uuid.uuid4()),
            timestamp=datetime.now(timezone.utc),
            debtor="Alice",
            creditor="Bob",
            currency="GBP",
            amount=Decimal("-10.00"),
        )


def test_transaction_rejects_self_debt() -> None:
    with pytest.raises(
        ValueError, match="Debtor and creditor cannot be the same entity"
    ):
        Transaction(
            id=str(uuid.uuid4()),
            timestamp=datetime.now(timezone.utc),
            debtor="Alice",
            creditor="Alice",
            currency="GBP",
            amount=Decimal("50.00"),
        )


def test_transaction_rejects_invalid_currency_format() -> None:
    with pytest.raises(
        ValueError, match="Currency must be a 3-letter uppercase string"
    ):
        Transaction(
            id=str(uuid.uuid4()),
            timestamp=datetime.now(timezone.utc),
            debtor="Alice",
            creditor="Bob",
            currency="gbp",
            amount=Decimal("50.00"),
        )


def test_transaction_rejects_naive_datetime() -> None:
    naive_dt = datetime.now()
    with pytest.raises(ValueError, match="Timestamp must be timezone-aware"):
        Transaction(
            id=str(uuid.uuid4()),
            timestamp=naive_dt,
            debtor="Alice",
            creditor="Bob",
            currency="GBP",
            amount=Decimal("50.00"),
        )


def test_transaction_rejects_invalid_uuid() -> None:
    with pytest.raises(
        ValueError, match="Transaction ID must be a valid UUIDv4 string"
    ):
        Transaction(
            id="DROP TABLE transactions",
            timestamp=datetime.now(timezone.utc),
            debtor="Alice",
            creditor="Bob",
            currency="GBP",
            amount=Decimal("50.00"),
        )
