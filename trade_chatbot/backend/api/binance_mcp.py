"""OAuth-enabled, fail-closed Binance MCP read-only endpoints."""

from __future__ import annotations

import os
import secrets

from flask import Blueprint, jsonify, redirect, request, session

from binance_agent_os.mcp import BinanceMCPClient, MCPError, ReadOnlyPolicyError
from binance_agent_os.oauth import (
    BinanceOAuthClient,
    InMemoryTokenStore,
    OAuthConfigurationError,
    OAuthExchangeError,
    generate_pkce,
)


binance_mcp_bp = Blueprint("binance_mcp", __name__)
token_store = InMemoryTokenStore()


def _enabled() -> bool:
    return os.environ.get("BINANCE_MCP_READ_ONLY_ENABLED", "false").lower() == "true"


def _client() -> BinanceMCPClient:
    timeout = float(os.environ.get("BINANCE_MCP_TIMEOUT_SECONDS", "20"))
    return BinanceMCPClient(timeout=timeout, access_token_provider=token_store.access_token)


def _oauth_client() -> BinanceOAuthClient:
    return BinanceOAuthClient(
        client_id=os.environ.get("BINANCE_MCP_CLIENT_ID", ""),
        redirect_uri=os.environ.get(
            "BINANCE_MCP_REDIRECT_URI",
            "http://127.0.0.1:5001/api/binance-mcp/oauth/callback",
        ),
        timeout=float(os.environ.get("BINANCE_MCP_TIMEOUT_SECONDS", "20")),
    )


def _disabled_response():
    return jsonify(
        {
            "error": "Binance MCP read-only PoC is disabled",
            "enable_with": "BINANCE_MCP_READ_ONLY_ENABLED=true",
        }
    ), 503


@binance_mcp_bp.get("/tools")
def list_tools():
    """Inventory tools and show the local read-only classification."""
    if not _enabled():
        return _disabled_response()
    try:
        inventory = [item.as_dict() for item in _client().inventory()]
        return jsonify(
            {
                "source": "https://agent.binance.com/mcp/agentic",
                "authenticated": token_store.access_token() is not None,
                "tools": inventory,
            }
        )
    except (MCPError, ValueError) as exc:
        return jsonify({"error": str(exc)}), 502


@binance_mcp_bp.get("/oauth/start")
def oauth_start():
    if not _enabled():
        return _disabled_response()
    try:
        verifier, challenge = generate_pkce()
        state = secrets.token_urlsafe(32)
        session["binance_oauth_state"] = state
        session["binance_oauth_verifier"] = verifier
        url = _oauth_client().authorization_url(
            state,
            challenge,
            scope=os.environ.get("BINANCE_MCP_OAUTH_SCOPE") or None,
        )
        return redirect(url)
    except OAuthConfigurationError as exc:
        return jsonify({"error": str(exc)}), 503


@binance_mcp_bp.get("/oauth/callback")
def oauth_callback():
    expected_state = session.pop("binance_oauth_state", None)
    verifier = session.pop("binance_oauth_verifier", None)
    state = request.args.get("state")
    code = request.args.get("code")
    if not expected_state or not state or not secrets.compare_digest(expected_state, state):
        return jsonify({"error": "OAuth state validation failed"}), 400
    if not code or not verifier:
        return jsonify({"error": "OAuth callback is missing code or PKCE verifier"}), 400
    try:
        token_store.set(_oauth_client().exchange_code(code, verifier))
        return jsonify({"authenticated": True, "message": "Binance MCP OAuth completed"})
    except (OAuthConfigurationError, OAuthExchangeError, ValueError) as exc:
        return jsonify({"error": str(exc)}), 502


@binance_mcp_bp.post("/oauth/disconnect")
def oauth_disconnect():
    token_store.clear()
    return jsonify({"authenticated": False})


@binance_mcp_bp.post("/market-data")
def market_data():
    """Call one server-advertised, read-only public-market tool."""
    if not _enabled():
        return _disabled_response()
    payload = request.get_json(silent=True) or {}
    tool = payload.get("tool")
    arguments = payload.get("arguments", {})
    if not isinstance(tool, str) or not tool:
        return jsonify({"error": "tool is required"}), 400
    if not isinstance(arguments, dict):
        return jsonify({"error": "arguments must be an object"}), 400
    try:
        result = _client().call_read_only(tool, arguments)
        return jsonify(
            {
                "source": "https://agent.binance.com/mcp/agentic",
                "tool": tool,
                "result": result,
            }
        )
    except ReadOnlyPolicyError as exc:
        return jsonify({"error": str(exc)}), 403
    except (MCPError, ValueError) as exc:
        return jsonify({"error": str(exc)}), 502
