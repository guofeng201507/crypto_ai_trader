"""Provider-neutral market data models."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Mapping, Optional, Sequence, Tuple


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def ensure_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


class MarketType(str, Enum):
    SPOT = "spot"
    FUTURES = "futures"


@dataclass(frozen=True)
class CanonicalSymbol:
    base: str
    quote: str
    market_type: MarketType = MarketType.SPOT

    def __post_init__(self) -> None:
        object.__setattr__(self, "base", self.base.upper())
        object.__setattr__(self, "quote", self.quote.upper())
        if not self.base or not self.quote:
            raise ValueError("base and quote are required")

    @classmethod
    def parse(cls, value: str, market_type: MarketType = MarketType.SPOT) -> "CanonicalSymbol":
        normalized = value.upper().strip()
        for separator in ("/", "-", "_"):
            if separator in normalized:
                base, quote = normalized.split(separator, 1)
                return cls(base, quote, market_type)
        for quote in ("USDT", "USDC", "BUSD", "USD", "BTC", "ETH", "EUR"):
            if normalized.endswith(quote) and len(normalized) > len(quote):
                return cls(normalized[: -len(quote)], quote, market_type)
        raise ValueError(f"Cannot parse trading symbol: {value}")

    def ccxt(self) -> str:
        return f"{self.base}/{self.quote}"

    def binance(self) -> str:
        return f"{self.base}{self.quote}"

    def yahoo(self) -> str:
        return f"{self.base}-{self.quote}"


@dataclass(frozen=True)
class MarketEvent:
    symbol: CanonicalSymbol
    source: str
    exchange_timestamp: Optional[datetime]
    received_at: datetime = field(default_factory=utc_now)
    request_id: Optional[str] = None
    raw: Mapping[str, Any] = field(default_factory=dict, repr=False, compare=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "received_at", ensure_utc(self.received_at))
        if self.exchange_timestamp is not None:
            object.__setattr__(self, "exchange_timestamp", ensure_utc(self.exchange_timestamp))

    def age_seconds(self, now: Optional[datetime] = None) -> Optional[float]:
        if self.exchange_timestamp is None:
            return None
        return max(0.0, (ensure_utc(now or utc_now()) - self.exchange_timestamp).total_seconds())


@dataclass(frozen=True)
class TickerSnapshot(MarketEvent):
    last: float = 0.0
    bid: Optional[float] = None
    ask: Optional[float] = None
    volume: Optional[float] = None
    change_percent: Optional[float] = None


@dataclass(frozen=True)
class OHLCVBar(MarketEvent):
    timeframe: str = ""
    open: float = 0.0
    high: float = 0.0
    low: float = 0.0
    close: float = 0.0
    volume: float = 0.0


@dataclass(frozen=True)
class OrderBookSnapshot(MarketEvent):
    bids: Sequence[Tuple[float, float]] = field(default_factory=tuple)
    asks: Sequence[Tuple[float, float]] = field(default_factory=tuple)


@dataclass(frozen=True)
class FundingSnapshot(MarketEvent):
    mark_price: float = 0.0
    index_price: float = 0.0
    last_funding_rate: float = 0.0


@dataclass(frozen=True)
class OpenInterestSnapshot(MarketEvent):
    open_interest: float = 0.0


@dataclass(frozen=True)
class AssetBalance:
    asset: str
    free: float = 0.0
    locked: float = 0.0

    @property
    def total(self) -> float:
        return self.free + self.locked


@dataclass(frozen=True)
class AccountBalanceSnapshot:
    source: str
    account_type: str
    balances: Sequence[AssetBalance]
    received_at: datetime = field(default_factory=utc_now)
    request_id: Optional[str] = None
    raw: Mapping[str, Any] = field(default_factory=dict, repr=False, compare=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "received_at", ensure_utc(self.received_at))
