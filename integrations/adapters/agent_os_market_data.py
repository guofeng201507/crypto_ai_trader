"""Agent OS adapter mapped onto project market-data DTOs.

Tool names remain configuration because the authenticated Binance tool inventory
is not available until the user completes OAuth. No guessed tool is called.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Mapping, Optional

from binance_agent_os.mcp import BinanceMCPClient
from integrations.domain import CanonicalSymbol, TickerSnapshot


class AgentOSToolMappingError(RuntimeError):
    pass


def _content_payload(result: Any) -> Mapping[str, Any]:
    if isinstance(result, Mapping):
        structured = result.get("structuredContent")
        if isinstance(structured, Mapping):
            return structured
        for item in result.get("content", []):
            if isinstance(item, Mapping) and item.get("type") == "text":
                text = item.get("text", "")
                try:
                    parsed = json.loads(text)
                    if isinstance(parsed, Mapping):
                        return parsed
                except (TypeError, json.JSONDecodeError):
                    continue
        return result
    raise ValueError("Agent OS tool result is not an object")


def _first(data: Mapping[str, Any], *keys: str):
    for key in keys:
        if data.get(key) is not None:
            return data[key]
    return None


class AgentOSMarketDataAdapter:
    def __init__(self, client: BinanceMCPClient, tool_mapping: Mapping[str, str]):
        self.client = client
        self.tool_mapping = dict(tool_mapping)

    def _tool(self, capability: str) -> str:
        name = self.tool_mapping.get(capability)
        if not name:
            raise AgentOSToolMappingError(
                f"No verified Agent OS tool mapped for capability: {capability}"
            )
        return name

    def get_ticker(self, exchange: str, symbol: CanonicalSymbol) -> TickerSnapshot:
        if exchange != "binance":
            raise ValueError("Agent OS adapter only supports Binance")
        result = self.client.call_read_only(
            self._tool("ticker"), {"symbol": symbol.binance()}
        )
        data = _content_payload(result)
        price = _first(data, "last", "lastPrice", "price", "close")
        if price is None:
            raise ValueError("Agent OS ticker result has no recognized price field")
        timestamp = _first(data, "timestamp", "closeTime", "time")
        exchange_timestamp: Optional[datetime] = None
        if timestamp is not None:
            exchange_timestamp = datetime.fromtimestamp(float(timestamp) / 1000, tz=timezone.utc)
        return TickerSnapshot(
            symbol=symbol,
            source="binance:agent-os",
            exchange_timestamp=exchange_timestamp,
            last=float(price),
            bid=float(data["bidPrice"]) if data.get("bidPrice") is not None else None,
            ask=float(data["askPrice"]) if data.get("askPrice") is not None else None,
            volume=float(_first(data, "volume", "baseVolume")) if _first(data, "volume", "baseVolume") is not None else None,
            change_percent=float(_first(data, "priceChangePercent", "percentage")) if _first(data, "priceChangePercent", "percentage") is not None else None,
            raw=data,
        )
