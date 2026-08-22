from datetime import datetime, timezone
from unittest.mock import AsyncMock, Mock
import asyncio

import pytest

from integrations.adapters.agent_os_market_data import AgentOSMarketDataAdapter, AgentOSToolMappingError
from integrations.adapters.agent_os_account import AgentOSAccountReadAdapter
from integrations.adapters.binance_futures import BinanceFuturesMetricsAdapter
from integrations.adapters.ccxt_market_data import CCXTMarketDataAdapter
from integrations.adapters.ccxt_order_book import CCXTOrderBookAdapter
from integrations.domain import CanonicalSymbol, MarketType, TickerSnapshot
from integrations.shadow import ShadowMarketDataComparator


def test_symbol_formats_are_canonical():
    symbol = CanonicalSymbol.parse("BTCUSDT", MarketType.FUTURES)
    assert symbol.ccxt() == "BTC/USDT"
    assert symbol.binance() == "BTCUSDT"
    assert symbol.yahoo() == "BTC-USDT"


def test_ccxt_adapter_normalizes_ticker_and_ohlcv():
    exchange = Mock()
    exchange.fetch_ticker.return_value = {
        "timestamp": 1_700_000_000_000, "last": 100.5, "bid": 100.0,
        "ask": 101.0, "baseVolume": 12.0, "percentage": 2.5,
    }
    exchange.fetch_ohlcv.return_value = [[1_700_000_000_000, 1, 2, 0.5, 1.5, 10]]
    adapter = CCXTMarketDataAdapter([], exchanges={"binance": exchange})
    symbol = CanonicalSymbol.parse("BTC/USDT")
    assert adapter.get_ticker("binance", symbol).last == 100.5
    assert adapter.get_ohlcv("binance", symbol, "1h")[0].close == 1.5


def test_order_book_adapter_preserves_timestamp_and_depth():
    exchange = Mock()
    exchange.markets = {"BTC/USDT": {}}
    exchange.fetch_order_book = AsyncMock(return_value={
        "timestamp": 1_700_000_000_000,
        "bids": [[100, 2]], "asks": [[101, 3]],
    })
    snapshot = asyncio.run(CCXTOrderBookAdapter("binance", exchange).get_order_book(
        CanonicalSymbol.parse("BTC/USDT"), 50
    ))
    assert snapshot.bids == ((100.0, 2.0),)
    exchange.fetch_order_book.assert_awaited_once_with("BTC/USDT", limit=50)


def test_futures_adapter_normalizes_public_metrics():
    session = Mock()
    responses = [
        {"symbol": "BTCUSDT", "markPrice": "100", "indexPrice": "99", "lastFundingRate": "0.001"},
        {"symbol": "BTCUSDT", "openInterest": "123"},
    ]
    mocked_responses = []
    for value in responses:
        response = Mock()
        response.json.return_value = value
        mocked_responses.append(response)
    session.get.side_effect = mocked_responses
    adapter = BinanceFuturesMetricsAdapter(session)
    symbol = CanonicalSymbol.parse("BTCUSDT", MarketType.FUTURES)
    assert adapter.get_funding(symbol).mark_price == 100
    assert adapter.get_open_interest(symbol).open_interest == 123


def test_agent_os_requires_verified_tool_mapping():
    adapter = AgentOSMarketDataAdapter(Mock(), {})
    with pytest.raises(AgentOSToolMappingError):
        adapter.get_ticker("binance", CanonicalSymbol.parse("BTCUSDT"))


def test_shadow_comparison_keeps_source_and_difference():
    symbol = CanonicalSymbol.parse("BTCUSDT")
    primary = Mock(get_ticker=Mock(return_value=TickerSnapshot(
        symbol=symbol, source="ccxt:binance", exchange_timestamp=datetime.now(timezone.utc), last=100
    )))
    shadow = Mock(get_ticker=Mock(return_value=TickerSnapshot(
        symbol=symbol, source="binance:agent-os", exchange_timestamp=datetime.now(timezone.utc), last=101
    )))
    result = ShadowMarketDataComparator(primary, shadow).compare_ticker("binance", symbol)
    assert result.absolute_difference == 1
    assert result.shadow_source == "binance:agent-os"


def test_agent_os_account_adapter_requires_verified_mapping():
    adapter = AgentOSAccountReadAdapter(Mock(), {})
    with pytest.raises(AgentOSToolMappingError):
        adapter.get_balances()


def test_agent_os_account_adapter_normalizes_balances():
    client = Mock()
    client.call_account_read_only.return_value = {
        "structuredContent": {
            "balances": [
                {"asset": "BTC", "free": "1.2", "locked": "0.3"},
                {"asset": "USDT", "availableBalance": "20"},
            ]
        }
    }
    mapping = {"account_spot_balances": "verified.account.balance"}
    result = AgentOSAccountReadAdapter(client, mapping).get_balances("spot")
    assert result.source == "binance:agent-os"
    assert result.balances[0].total == 1.5
    assert result.balances[1].free == 20
    client.call_account_read_only.assert_called_once_with(
        "verified.account.balance", {}, allowed_tools=("verified.account.balance",)
    )
