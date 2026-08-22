import json

import pytest

from binance_agent_os.mcp.client import (
    BinanceMCPClient,
    ReadOnlyPolicyError,
    contains_sensitive_key,
    redact,
)


class FakeResponse:
    def __init__(self, payload, headers=None, content_type="application/json"):
        self._payload = payload
        self.headers = {"Content-Type": content_type, **(headers or {})}
        self.status_code = 200
        self.text = json.dumps(payload)

    def raise_for_status(self):
        return None

    def json(self):
        return self._payload


class FakeSession:
    def __init__(self, tools):
        self.tools = tools
        self.calls = []
        self.headers = []

    def post(self, url, headers, json, timeout):
        self.calls.append(json)
        self.headers.append(headers)
        method = json["method"]
        if method == "initialize":
            return FakeResponse(
                {"jsonrpc": "2.0", "id": json["id"], "result": {}},
                {"Mcp-Session-Id": "test-session"},
            )
        if method == "notifications/initialized":
            return FakeResponse({"jsonrpc": "2.0"})
        if method == "tools/list":
            return FakeResponse(
                {"jsonrpc": "2.0", "id": json["id"], "result": {"tools": self.tools}}
            )
        if method == "tools/call":
            return FakeResponse(
                {
                    "jsonrpc": "2.0",
                    "id": json["id"],
                    "result": {"content": [{"type": "text", "text": "123.45"}]},
                }
            )
        raise AssertionError(method)


def tool(name, description, read_only):
    return {
        "name": name,
        "description": description,
        "inputSchema": {"type": "object"},
        "annotations": {"readOnlyHint": read_only},
    }


def test_inventory_and_call_allow_public_market_tool():
    session = FakeSession([tool("get_ticker", "Current market price", True)])
    client = BinanceMCPClient(session=session)

    inventory = client.inventory()
    assert inventory[0].read_only_eligible is True
    result = client.call_read_only("get_ticker", {"symbol": "BTCUSDT"})

    assert result["content"][0]["text"] == "123.45"
    assert session.calls[-1]["method"] == "tools/call"


@pytest.mark.parametrize(
    "candidate",
    [
        tool("place_order", "Buy at market", False),
        tool("get_balance", "Read account balance", True),
        tool("get_ticker", "Current market price", False),
    ],
)
def test_policy_blocks_write_private_or_unannotated_tools(candidate):
    client = BinanceMCPClient(session=FakeSession([candidate]))
    with pytest.raises(ReadOnlyPolicyError):
        client.call_read_only(candidate["name"], {})


def test_redact_removes_nested_credentials():
    assert redact({"symbol": "BTCUSDT", "api_key": "secret", "nested": {"token": "x"}}) == {
        "symbol": "BTCUSDT",
        "api_key": "[REDACTED]",
        "nested": {"token": "[REDACTED]"},
    }


def test_sensitive_detection_checks_keys_not_market_values():
    assert contains_sensitive_key({"symbol": "TOKENUSDT"}) is False
    assert contains_sensitive_key({"nested": {"access_token": "x"}}) is True


def test_only_official_endpoint_is_allowed():
    with pytest.raises(ValueError):
        BinanceMCPClient(endpoint="https://example.com/mcp")


def test_account_read_requires_explicit_allowlist_and_read_only_annotation():
    account_tool = tool("get_balance", "Read account balance", True)
    client = BinanceMCPClient(session=FakeSession([account_tool]))

    with pytest.raises(ReadOnlyPolicyError):
        client.call_account_read_only("get_balance", {}, allowed_tools=[])

    result = client.call_account_read_only(
        "get_balance", {}, allowed_tools=["get_balance"]
    )
    assert result["content"][0]["text"] == "123.45"


@pytest.mark.parametrize(
    "candidate",
    [
        tool("transfer_asset", "Transfer account balance", True),
        tool("get_balance", "Read account balance", False),
    ],
)
def test_account_read_blocks_write_or_unannotated_tool(candidate):
    client = BinanceMCPClient(session=FakeSession([candidate]))
    with pytest.raises(ReadOnlyPolicyError):
        client.call_account_read_only(
            candidate["name"], {}, allowed_tools=[candidate["name"]]
        )


def test_bearer_token_is_added_without_logging_or_payload_injection():
    session = FakeSession([tool("get_ticker", "Current market price", True)])
    client = BinanceMCPClient(
        session=session, access_token_provider=lambda: "oauth-secret"
    )
    client.inventory()
    assert session.headers[0]["Authorization"] == "Bearer oauth-secret"
    assert "oauth-secret" not in json.dumps(session.calls)
