"""Shared synchronous CCXT market-data adapter."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict, Iterable, Mapping, Optional, Sequence

import ccxt

from integrations.domain import CanonicalSymbol, MarketType, OHLCVBar, TickerSnapshot


def _timestamp(value) -> Optional[datetime]:
    if value is None:
        return None
    return datetime.fromtimestamp(float(value) / 1000, tz=timezone.utc)


class CCXTMarketDataAdapter:
    def __init__(self, exchange_names: Iterable[str], exchanges: Optional[Mapping[str, object]] = None):
        self.exchanges: Dict[str, object] = dict(exchanges or {})
        for name in exchange_names:
            if name not in self.exchanges:
                exchange_class = getattr(ccxt, name)
                self.exchanges[name] = exchange_class(
                    {
                        "enableRateLimit": True,
                        "timeout": 30000,
                        "options": {"adjustForTimeDifference": True},
                    }
                )

    def _exchange(self, name: str):
        if name not in self.exchanges:
            raise ValueError(f"Exchange {name} not initialized")
        return self.exchanges[name]

    def list_symbols(self, exchange: str) -> Sequence[CanonicalSymbol]:
        markets = self._exchange(exchange).load_markets()
        results = []
        for market in markets.values():
            base, quote = market.get("base"), market.get("quote")
            if base and quote:
                market_type = MarketType.FUTURES if market.get("contract") else MarketType.SPOT
                results.append(CanonicalSymbol(base, quote, market_type))
        return results

    def get_ticker(self, exchange: str, symbol: CanonicalSymbol) -> TickerSnapshot:
        raw = self._exchange(exchange).fetch_ticker(symbol.ccxt())
        last = raw.get("last") if raw.get("last") is not None else raw.get("close")
        if last is None:
            raise ValueError(f"Ticker has no last/close price for {symbol.ccxt()}")
        return TickerSnapshot(
            symbol=symbol,
            source=f"ccxt:{exchange}",
            exchange_timestamp=_timestamp(raw.get("timestamp")),
            last=float(last),
            bid=float(raw["bid"]) if raw.get("bid") is not None else None,
            ask=float(raw["ask"]) if raw.get("ask") is not None else None,
            volume=float(raw["baseVolume"]) if raw.get("baseVolume") is not None else None,
            change_percent=float(raw["percentage"]) if raw.get("percentage") is not None else None,
            raw=raw,
        )

    def get_ohlcv(
        self,
        exchange: str,
        symbol: CanonicalSymbol,
        timeframe: str,
        since: Optional[datetime] = None,
        limit: Optional[int] = None,
    ) -> Sequence[OHLCVBar]:
        since_ms = int(since.timestamp() * 1000) if since else None
        rows = self._exchange(exchange).fetch_ohlcv(
            symbol.ccxt(), timeframe, since=since_ms, limit=limit
        )
        return [
            OHLCVBar(
                symbol=symbol,
                source=f"ccxt:{exchange}",
                exchange_timestamp=_timestamp(row[0]),
                timeframe=timeframe,
                open=float(row[1]),
                high=float(row[2]),
                low=float(row[3]),
                close=float(row[4]),
                volume=float(row[5]),
                raw={"row": row},
            )
            for row in rows
        ]
