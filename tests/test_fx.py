from decimal import Decimal

from src.fx import StaticFXProvider, detect_arbitrage


def test_detect_arbitrage_finds_profitable_cycle() -> None:
    """
    Test that the Bellman-Ford algorithm successfully detects a
    multiplicative arbitrage cycle using negative logarithms.
    """
    # Arrange: A triangle arbitrage opportunity.
    # Start with 1.0 GBP.
    # 1.0 GBP -> 1.20 EUR
    # 1.20 EUR -> 1.25 USD (1.20 * 1.25 = 1.50 USD)
    # 1.50 USD -> 0.70 GBP (1.50 * 0.70 = 1.05 GBP)
    # 1.05 GBP > 1.0 GBP. Arbitrage exists.

    rates = {
        ("GBP", "EUR"): Decimal("1.20"),
        ("EUR", "USD"): Decimal("1.25"),
        ("USD", "GBP"): Decimal("0.70"),
    }
    provider = StaticFXProvider(rates)

    # We must pass the known currencies in the network
    currencies = ["GBP", "EUR", "USD"]

    # Act
    has_arbitrage = detect_arbitrage(provider, currencies)

    # Assert
    assert has_arbitrage is True


def test_detect_arbitrage_ignores_safe_network() -> None:
    """
    Test that the algorithm returns False when no arbitrage exists.
    """
    # 1.0 GBP -> 1.0 EUR -> 1.0 USD -> 1.0 GBP
    rates = {
        ("GBP", "EUR"): Decimal("1.00"),
        ("EUR", "USD"): Decimal("1.00"),
        ("USD", "GBP"): Decimal("1.00"),
    }
    provider = StaticFXProvider(rates)
    currencies = ["GBP", "EUR", "USD"]

    assert detect_arbitrage(provider, currencies) is False
