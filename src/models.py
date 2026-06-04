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
