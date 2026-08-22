"""Provider-neutral async order-book adapter around CCXT exchanges."""

from datetime import datetime, timezone

from integrations.domain import CanonicalSymbol, OrderBookSnapshot


class CCXTOrderBookAdapter:
    def __init__(self, exchange_name: str, exchange):
        self.exchange_name = exchange_name
        self.exchange = exchange

    async def get_order_book(self, symbol: CanonicalSymbol, depth: int = 50):
        if not self.exchange.markets:
            await self.exchange.load_markets()
        ccxt_symbol = symbol.ccxt()
        if ccxt_symbol not in self.exchange.markets:
            raise ValueError(f"Symbol {ccxt_symbol} not available on {self.exchange_name}")
        raw = await self.exchange.fetch_order_book(ccxt_symbol, limit=depth)
        timestamp = raw.get("timestamp")
        exchange_timestamp = datetime.fromtimestamp(timestamp / 1000, tz=timezone.utc) if timestamp else None
        return OrderBookSnapshot(
            symbol=symbol, source=f"ccxt:{self.exchange_name}",
            exchange_timestamp=exchange_timestamp,
            bids=tuple((float(p), float(a)) for p, a, *_ in raw.get("bids", [])),
            asks=tuple((float(p), float(a)) for p, a, *_ in raw.get("asks", [])),
            raw=raw,
        )
