"""Backward-compatible market data facade for the price monitor."""

from integrations.legacy_data_fetcher import LegacyDataFetcher


class DataFetcher(LegacyDataFetcher):
    """Shared CCXT adapter exposed through the original monitor API."""
