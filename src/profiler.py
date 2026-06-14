import random
import time
import tracemalloc
import uuid
from datetime import datetime, timezone
from decimal import Decimal

from src.engine import calculate_net_balances
from src.models import Transaction


def generate_synthetic_ledger(num_transactions: int) -> list[Transaction]:
    """
    Generates a deterministic stochastic graph of transactions to simulate
    massive supply chain networks or global financial ledgers.
    """
    # Create a pool of entities (e.g., 10% of transaction count
    # to ensure density/cycles)
    num_entities = max(5, num_transactions // 10)
    entities = [f"Hub_{i}" for i in range(num_entities)]

    ledger = []
    for _ in range(num_transactions):
        debtor, creditor = random.sample(entities, 2)
        ledger.append(
            Transaction(
                id=str(uuid.uuid4()),
                timestamp=datetime.now(timezone.utc),
                debtor=debtor,
                creditor=creditor,
                currency="USD",
                amount=Decimal(str(round(random.uniform(10.0, 10000.0), 2))),
            )
        )
    return ledger


def run_profiler() -> None:
    """
    Executes the netting engine across exponentially scaling data volumes,
    recording hardware latency (ms) and peak RAM allocation (MB).
    """
    # Scale from 10 nodes up to 1,000,000 nodes
    node_counts = [10, 100, 1000, 10000, 100000, 1000000]

    print(f"\n{'Transactions':<15} | {'Latency (ms)':<15} | {'Peak RAM (MB)':<15}")
    print("-" * 50)

    for count in node_counts:
        # 1. Arrange: Generate the massive dataset
        ledger = generate_synthetic_ledger(count)

        # 2. Instrument: Start memory and time tracking
        tracemalloc.start()
        start_time = time.perf_counter()

        # 3. Act: Execute the mathematical core
        calculate_net_balances(ledger)

        # 4. Measure: Capture metrics
        end_time = time.perf_counter()
        _, peak_memory = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        # 5. Calculate formatting
        elapsed_ms = (end_time - start_time) * 1000
        peak_mb = peak_memory / (1024 * 1024)

        print(f"{count:<15} | {elapsed_ms:<15.2f} | {peak_mb:<15.2f}")


if __name__ == "__main__":
    run_profiler()
