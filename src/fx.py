from decimal import Decimal
from typing import Dict, Protocol, Tuple


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
