"""Provider adapter for Binance public USD-M Futures metrics."""

from __future__ import annotations

from typing import Optional, Sequence

import requests

from integrations.domain import CanonicalSymbol, FundingSnapshot, MarketType, OpenInterestSnapshot


class BinanceFuturesMetricsAdapter:
    BASE_URL = "https://fapi.binance.com"

    def __init__(self, session: Optional[requests.Session] = None, timeout: float = 10):
        self.session = session or requests.Session()
        self.timeout = timeout

    def _get(self, path: str, params=None):
        response = self.session.get(
            f"{self.BASE_URL}{path}", params=params, timeout=self.timeout
        )
        response.raise_for_status()
        return response.json()

    def list_usdt_perpetual_symbols(self) -> Sequence[CanonicalSymbol]:
        data = self._get("/fapi/v1/exchangeInfo")
        return [
            CanonicalSymbol(
                item.get("baseAsset") or CanonicalSymbol.parse(item["symbol"]).base,
                item["quoteAsset"],
                MarketType.FUTURES,
            )
            for item in data.get("symbols", [])
            if item.get("contractType") == "PERPETUAL"
            and item.get("quoteAsset") == "USDT"
            and item.get("status") == "TRADING"
        ]

    def get_funding(self, symbol: CanonicalSymbol) -> FundingSnapshot:
        data = self._get("/fapi/v1/premiumIndex", {"symbol": symbol.binance()})
        return FundingSnapshot(
            symbol=CanonicalSymbol(symbol.base, symbol.quote, MarketType.FUTURES),
            source="binance:fapi",
            exchange_timestamp=None,
            mark_price=float(data["markPrice"]),
            index_price=float(data["indexPrice"]),
            last_funding_rate=float(data["lastFundingRate"]),
            raw=data,
        )

    def get_open_interest(self, symbol: CanonicalSymbol) -> OpenInterestSnapshot:
        data = self._get("/fapi/v1/openInterest", {"symbol": symbol.binance()})
        return OpenInterestSnapshot(
            symbol=CanonicalSymbol(symbol.base, symbol.quote, MarketType.FUTURES),
            source="binance:fapi",
            exchange_timestamp=None,
            open_interest=float(data["openInterest"]),
            raw=data,
        )

    def get_ratio(self, endpoint: str, symbol: CanonicalSymbol, value_key: str, period="5m"):
        allowed = {
            "globalLongShortAccountRatio",
            "topLongShortAccountRatio",
            "topLongShortPositionRatio",
            "takerlongshortRatio",
        }
        if endpoint not in allowed:
            raise ValueError("Unsupported Binance Futures ratio endpoint")
        data = self._get(
            f"/futures/data/{endpoint}",
            {"symbol": symbol.binance(), "period": period, "limit": 1},
        )
        if not data:
            return None
        value = data[-1].get(value_key)
        return float(value) if value is not None else None
