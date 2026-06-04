from collections import defaultdict
from decimal import Decimal
from typing import Dict, List

from src.models import Transaction


def calculate_net_balances(transactions: List[Transaction]) -> Dict[str, Decimal]:
    """
    Aggregates a list of transactions into a net balance dictionary.
    Time Complexity: O(N) where N is the number of transactions.
    """
    # defaultdict automatically initialises missing keys with Decimal("0")
    balances: Dict[str, Decimal] = defaultdict(Decimal)

    for tx in transactions:
        balances[tx.debtor] -= tx.amount
        balances[tx.creditor] += tx.amount

    # Convert back to a standard dictionary to satisfy the strict return type
    return dict(balances)
