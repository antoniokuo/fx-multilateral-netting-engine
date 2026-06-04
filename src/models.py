from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass(frozen=True)
class Transaction:
    id: str
    timestamp: datetime
    debtor: str
    creditor: str
    currency: str
    amount: Decimal

    def __post_init__(self) -> None:
        if self.amount <= Decimal("0"):
            raise ValueError("Amount must be strictly positive")

        if self.debtor == self.creditor:
            raise ValueError("Debtor and creditor cannot be the same entity")

        if (
            not isinstance(self.currency, str)
            or len(self.currency) != 3
            or not self.currency.isupper()
            or not self.currency.isalpha()
        ):
            raise ValueError("Currency must be a 3-letter uppercase string")
