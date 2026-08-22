"""Compare two read providers without changing the primary result."""

from dataclasses import asdict, dataclass
from typing import Optional

from integrations.domain import CanonicalSymbol, TickerSnapshot


@dataclass(frozen=True)
class TickerComparison:
    symbol: str
    primary_source: str
    shadow_source: str
    primary_price: float
    shadow_price: float
    absolute_difference: float
    difference_bps: float
    primary_age_seconds: Optional[float]
    shadow_age_seconds: Optional[float]

    def as_dict(self):
        return asdict(self)


class ShadowMarketDataComparator:
    def __init__(self, primary, shadow):
        self.primary = primary
        self.shadow = shadow

    def compare_ticker(self, exchange: str, symbol: CanonicalSymbol) -> TickerComparison:
        primary: TickerSnapshot = self.primary.get_ticker(exchange, symbol)
        shadow: TickerSnapshot = self.shadow.get_ticker(exchange, symbol)
        difference = abs(primary.last - shadow.last)
        midpoint = (primary.last + shadow.last) / 2
        return TickerComparison(
            symbol=symbol.ccxt(), primary_source=primary.source, shadow_source=shadow.source,
            primary_price=primary.last, shadow_price=shadow.last,
            absolute_difference=difference,
            difference_bps=(difference / midpoint * 10000) if midpoint else 0.0,
            primary_age_seconds=primary.age_seconds(), shadow_age_seconds=shadow.age_seconds(),
        )
