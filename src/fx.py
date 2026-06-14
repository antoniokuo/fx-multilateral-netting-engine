import math
from decimal import Decimal
from typing import Dict, List, Protocol, Tuple


class FXProvider(Protocol):
    """
    Abstract contract for exchange rate resolution.
    Any class injected into the routing engine must fulfill this signature.
    """

    def get_rate(self, base_currency: str, target_currency: str) -> Decimal: ...


class StaticFXProvider:
    """
    Deterministic rate provider for testing and fixed-rate netting.
    """

    def __init__(self, rates: Dict[Tuple[str, str], Decimal]) -> None:
        # Dictionary maps (base_currency, target_currency) -> Decimal rate
        self._rates = rates

    def get_rate(self, base_currency: str, target_currency: str) -> Decimal:
        if base_currency == target_currency:
            return Decimal("1.0000")

        rate = self._rates.get((base_currency, target_currency))
        if rate is None:
            raise ValueError(
                f"No exchange rate found for {base_currency} to {target_currency}"
            )

        return rate


def detect_arbitrage(fx_provider: FXProvider, currencies: List[str]) -> bool:
    """
    Detects risk-free arbitrage cycles in an FX network using the
    Bellman-Ford algorithm. Transforms multiplicative exchange rates
    into additive edge weights via negative logarithms.
    """
    # 1. Build the directed graph
    edges: List[Tuple[str, str, float]] = []

    for u in currencies:
        for v in currencies:
            if u == v:
                continue
            try:
                rate = fx_provider.get_rate(base_currency=u, target_currency=v)
                # The Logarithmic Trick: -ln(rate)
                weight = -math.log(float(rate))
                edges.append((u, v, weight))
            except ValueError:
                # If no direct market rate exists between the pair, ignore the edge
                pass

    # 2. Initialise distances
    # We initialise all nodes to 0.0 because the arbitrage cycle could
    # exist anywhere in the network, not just from a single source node.
    distances: Dict[str, float] = {currency: 0.0 for currency in currencies}
    v_count = len(currencies)

    # 3. The Core Bellman-Ford Relaxation (V - 1 times)
    for _ in range(v_count - 1):
        for u, v, weight in edges:
            if distances[u] + weight < distances[v]:
                distances[v] = distances[u] + weight

    # 4. The Nth Relaxation (Detecting the Negative Cycle)
    # We use a tiny tolerance (1e-9) to prevent standard IEEE-754
    # floating-point math inaccuracies from triggering false positives.
    for u, v, weight in edges:
        if distances[u] + weight < distances[v] - 1e-9:
            return True

    return False
