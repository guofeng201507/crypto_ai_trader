from unittest.mock import patch

from binance_agent_os.mcp.client import ToolInventoryItem
from trade_chatbot.backend.app import create_app
from trade_chatbot.backend.api.binance_mcp import token_store


def test_gateway_is_disabled_by_default(monkeypatch):
    monkeypatch.delenv("BINANCE_MCP_READ_ONLY_ENABLED", raising=False)
    client = create_app().test_client()
    response = client.get("/api/binance-mcp/tools")
    assert response.status_code == 503


def test_inventory_endpoint_exposes_policy_result(monkeypatch):
    monkeypatch.setenv("BINANCE_MCP_READ_ONLY_ENABLED", "true")
    item = ToolInventoryItem(
        name="get_ticker",
        description="Current market price",
        input_schema={"type": "object"},
        annotations={"readOnlyHint": True},
        read_only_eligible=True,
        policy_reason="safe",
    )
    with patch(
        "trade_chatbot.backend.api.binance_mcp.BinanceMCPClient.inventory",
        return_value=[item],
    ):
        response = create_app().test_client().get("/api/binance-mcp/tools")
    assert response.status_code == 200
    assert response.get_json()["tools"][0]["name"] == "get_ticker"
    assert response.get_json()["authenticated"] is False


def test_market_endpoint_rejects_invalid_payload(monkeypatch):
    monkeypatch.setenv("BINANCE_MCP_READ_ONLY_ENABLED", "true")
    response = create_app().test_client().post(
        "/api/binance-mcp/market-data", json={"arguments": {}}
    )
    assert response.status_code == 400


def test_oauth_start_uses_pkce_and_callback_validates_state(monkeypatch):
    monkeypatch.setenv("BINANCE_MCP_READ_ONLY_ENABLED", "true")
    monkeypatch.setenv("BINANCE_MCP_CLIENT_ID", "client-id")
    client = create_app().test_client()
    response = client.get("/api/binance-mcp/oauth/start")
    assert response.status_code == 302
    assert "code_challenge_method=S256" in response.location

    bad_callback = client.get(
        "/api/binance-mcp/oauth/callback?state=wrong&code=code"
    )
    assert bad_callback.status_code == 400


def test_oauth_disconnect_clears_token():
    token_store.clear()
    response = create_app().test_client().post(
        "/api/binance-mcp/oauth/disconnect"
    )
    assert response.status_code == 200
    assert response.get_json()["authenticated"] is False
