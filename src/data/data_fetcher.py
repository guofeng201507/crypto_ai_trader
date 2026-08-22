"""Backward-compatible market data facade for the core application."""

from integrations.legacy_data_fetcher import LegacyDataFetcher


class DataFetcher(LegacyDataFetcher):
    """Shared CCXT adapter exposed through the original API."""


def main():
    fetcher = DataFetcher(["binance"])
    print(fetcher.fetch_ohlcv("binance", "BTC/USDT", "1h", 100).head())


if __name__ == "__main__":
    main()
