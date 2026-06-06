import logging
import uuid
from collections import defaultdict
from datetime import datetime, timezone
from decimal import Decimal
from typing import Dict, List, Tuple

from src.models import Transaction

# Initialise the module-level logger
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO, format="[%(levelname)s] %(asctime)s - %(name)s: %(message)s"
)


def calculate_net_balances(
    transactions: List[Transaction],
) -> Dict[str, Dict[str, Decimal]]:
    """
    Aggregates a list of transactions into a net balance dictionary grouped by currency.
    Returns: Dict[currency, Dict[entity, net_balance]]
    Time Complexity: O(N) where N is the number of transactions.
    """
    logger.info(f"Calculating net balances for {len(transactions)} transactions.")

    # Outer dict maps Currency -> Inner dict (Entity -> Balance)
    balances: Dict[str, Dict[str, Decimal]] = {}

    for tx in transactions:
        # Initialise the currency graph if it doesn't exist
        if tx.currency not in balances:
            balances[tx.currency] = defaultdict(Decimal)

        # Execute the zero-sum math within the isolated currency boundary
        balances[tx.currency][tx.debtor] -= tx.amount
        balances[tx.currency][tx.creditor] += tx.amount

    # Convert the inner defaultdicts back to standard dicts for strict type compliance
    return {
        currency: dict(entity_balances)
        for currency, entity_balances in balances.items()
    }


def route_settlement(balances: Dict[str, Decimal], currency: str) -> List[Transaction]:
    """
    Resolves a net balance dictionary into the minimum number of transactions
    using a greedy minimum cash flow algorithm.
    """
    logger.info(
        f"Initiating minimum cash flow routing for {len(balances)} active entities."
    )
    # 1. Partitioning: Separate entities into debtors and creditors.
    # Ignore anyone with a balance of exactly Decimal("0").
    # Store them as lists of lists: [[entity_name, absolute_amount], ...]
    # Example: debtors = [["Alice", Decimal("30.00")], ["Charlie", Decimal("10.00")]]
    debtors: List[Tuple[str, Decimal]] = []
    creditors: List[Tuple[str, Decimal]] = []

    for entity, balance in balances.items():
        if balance < Decimal("0"):
            debtors.append((entity, abs(balance)))
        elif balance > Decimal("0"):
            creditors.append((entity, balance))

    # 2. Sorting: Sort both lists in descending order based on the amount.
    # This ensures processing the largest debts and credits first (The Greedy approach).
    debtors.sort(key=lambda x: x[1], reverse=True)
    creditors.sort(key=lambda x: x[1], reverse=True)

    settlements: List[Transaction] = []

    # 3. The Routing Loop
    # Continue looping as long as both the debtors and creditors lists are not empty.

    # Initialise pointers at the start of both lists
    debtor_idx = 0
    creditor_idx = 0

    # Continue as long as both pointers are within bounds
    while debtor_idx < len(debtors) and creditor_idx < len(creditors):
        # Access elements using the pointers
        debtor_name, debtor_amount = debtors[debtor_idx]
        creditor_name, creditor_amount = creditors[creditor_idx]

        settlement_amount = min(debtor_amount, creditor_amount)

        logger.debug(
            f"Routing {settlement_amount} {currency} from {debtor_name} to {creditor_name}"
        )

        new_transaction = Transaction(
            id=str(uuid.uuid4()),
            timestamp=datetime.now(timezone.utc),
            debtor=debtor_name,
            creditor=creditor_name,
            currency=currency,
            amount=settlement_amount,
        )

        settlements.append(new_transaction)

        # Calculate new balances
        new_debtor_amount = debtor_amount - settlement_amount
        new_creditor_amount = creditor_amount - settlement_amount

        # Reassign immutable tuples back to the array
        debtors[debtor_idx] = (debtor_name, new_debtor_amount)
        creditors[creditor_idx] = (creditor_name, new_creditor_amount)

        # If a balance hits zero, advance the pointer instead of shifting the array
        # Advance pointers if the balance is zero
        if new_debtor_amount == Decimal("0"):
            debtor_idx += 1

        if new_creditor_amount == Decimal("0"):
            creditor_idx += 1

    return settlements
