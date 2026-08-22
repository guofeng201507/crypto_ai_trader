"""Ports consumed by strategies, monitors and research code."""

from __future__ import annotations

from datetime import datetime
from typing import Optional, Protocol, Sequence

from integrations.domain import (
    AccountBalanceSnapshot,
    CanonicalSymbol,
    FundingSnapshot,
    OHLCVBar,
    OpenInterestSnapshot,
    OrderBookSnapshot,
    TickerSnapshot,
)


class MarketDataPort(Protocol):
    def get_ticker(self, exchange: str, symbol: CanonicalSymbol) -> TickerSnapshot: ...
    def list_symbols(self, exchange: str) -> Sequence[CanonicalSymbol]: ...


class HistoricalDataPort(Protocol):
    def get_ohlcv(
        self,
        exchange: str,
        symbol: CanonicalSymbol,
        timeframe: str,
        since: Optional[datetime] = None,
        limit: Optional[int] = None,
    ) -> Sequence[OHLCVBar]: ...


class OrderBookPort(Protocol):
    async def get_order_book(
        self, exchange: str, symbol: CanonicalSymbol, depth: int
    ) -> OrderBookSnapshot: ...


class FuturesMetricsPort(Protocol):
    def get_funding(self, symbol: CanonicalSymbol) -> FundingSnapshot: ...
    def get_open_interest(self, symbol: CanonicalSymbol) -> OpenInterestSnapshot: ...


class AccountReadPort(Protocol):
    def get_balances(self, account_type: str = "spot") -> AccountBalanceSnapshot: ...
