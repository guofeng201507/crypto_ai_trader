"""Backward-compatible facade over the shared CCXT adapter."""

from datetime import datetime, timedelta, timezone
from typing import List, Optional

import pandas as pd
from loguru import logger

from integrations.adapters import CCXTMarketDataAdapter
from integrations.domain import CanonicalSymbol


class LegacyDataFetcher:
    def __init__(self, exchange_names: List[str]):
        try:
            self.adapter = CCXTMarketDataAdapter(exchange_names)
            self.exchanges = self.adapter.exchanges
        except Exception as exc:
            logger.error(f"Failed to initialize exchanges: {exc}")
            self.adapter = CCXTMarketDataAdapter([], exchanges={})
            self.exchanges = self.adapter.exchanges

    @staticmethod
    def _frame(bars) -> pd.DataFrame:
        if not bars:
            return pd.DataFrame()
        frame = pd.DataFrame([{
            "timestamp": bar.exchange_timestamp,
            "open": bar.open, "high": bar.high, "low": bar.low,
            "close": bar.close, "volume": bar.volume,
        } for bar in bars])
        frame.set_index("timestamp", inplace=True)
        if getattr(frame.index, "tz", None) is not None:
            frame.index = frame.index.tz_convert("UTC").tz_localize(None)
        return frame

    def fetch_ohlcv(self, exchange_name, symbol, timeframe="1h", limit=100):
        try:
            return self._frame(self.adapter.get_ohlcv(
                exchange_name, CanonicalSymbol.parse(symbol), timeframe, limit=limit
            ))
        except Exception as exc:
            logger.error(f"Failed to fetch data from {exchange_name} for {symbol}: {exc}")
            return pd.DataFrame()

    def fetch_historical_data(self, exchange_name, symbol, days=90, timeframe="1d"):
        try:
            since = datetime.now(timezone.utc) - timedelta(days=days)
            return self._frame(self.adapter.get_ohlcv(
                exchange_name, CanonicalSymbol.parse(symbol), timeframe, since=since
            ))
        except Exception as exc:
            logger.error(f"Error fetching historical data for {symbol} on {exchange_name}: {exc}")
            return pd.DataFrame()

    def get_available_symbols(self, exchange_name):
        try:
            return [item.ccxt() for item in self.adapter.list_symbols(exchange_name)]
        except Exception as exc:
            logger.error(f"Failed to fetch symbols from {exchange_name}: {exc}")
            return []

    def fetch_multiple_exchanges(self, symbols, days=90, timeframe="1d"):
        return {exchange: {
            symbol: self.fetch_historical_data(exchange, symbol, days, timeframe)
            for symbol in symbols
        } for exchange in self.exchanges}

    def get_current_price(self, exchange_name, symbol) -> Optional[float]:
        try:
            return self.adapter.get_ticker(exchange_name, CanonicalSymbol.parse(symbol)).last
        except Exception as exc:
            logger.error(f"Error fetching current price for {symbol} on {exchange_name}: {exc}")
            return None
