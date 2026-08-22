"""Streamable HTTP MCP client with OAuth injection and fail-closed policies."""

from __future__ import annotations

import json
import logging
import re
import time
import uuid
from dataclasses import dataclass
from typing import Any, Callable, Dict, Iterable, List, Mapping, Optional

import requests


DEFAULT_ENDPOINT = "https://agent.binance.com/mcp/agentic"
PROTOCOL_VERSION = "2025-03-26"

# A tool must look market-data related and must not look account/action related.
_MARKET_TERMS = re.compile(
    r"(market|ticker|price|quote|order.?book|depth|candle|kline|funding|symbol|exchange.?info)",
    re.IGNORECASE,
)
_WRITE_OR_PRIVATE_TERMS = re.compile(
    r"(trade|order|buy|sell|cancel|convert|transfer|withdraw|deposit|account|balance|position|bill|wallet|margin)",
    re.IGNORECASE,
)
_WRITE_TERMS = re.compile(
    r"(create|place|trade|buy|sell|cancel|convert|transfer|withdraw|deposit|borrow|repay)",
    re.IGNORECASE,
)
_SENSITIVE_KEY = re.compile(
    r"(authorization|token|secret|api.?key|password|cookie|signature)", re.IGNORECASE
)

logger = logging.getLogger(__name__)


class MCPError(RuntimeError):
    """Raised when the remote MCP server returns an invalid/error response."""


class ReadOnlyPolicyError(MCPError):
    """Raised when a tool is not demonstrably safe for its read-only gateway."""


@dataclass(frozen=True)
class ToolInventoryItem:
    name: str
    description: str
    input_schema: Mapping[str, Any]
    annotations: Mapping[str, Any]
    read_only_eligible: bool
    policy_reason: str

    def as_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": dict(self.input_schema),
            "annotations": dict(self.annotations),
            "read_only_eligible": self.read_only_eligible,
            "policy_reason": self.policy_reason,
        }


def redact(value: Any) -> Any:
    """Recursively redact credential-like fields before audit logging."""
    if isinstance(value, Mapping):
        return {
            str(key): "[REDACTED]" if _SENSITIVE_KEY.search(str(key)) else redact(item)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [redact(item) for item in value]
    return value


def contains_sensitive_key(value: Any) -> bool:
    """Return True for credential-shaped field names without scanning values."""
    if isinstance(value, Mapping):
        return any(
            _SENSITIVE_KEY.search(str(key)) or contains_sensitive_key(item)
            for key, item in value.items()
        )
    if isinstance(value, list):
        return any(contains_sensitive_key(item) for item in value)
    return False


class BinanceMCPClient:
    """MCP client supporting public-market and explicit account-read policies."""

    def __init__(
        self,
        endpoint: str = DEFAULT_ENDPOINT,
        timeout: float = 20.0,
        session: Optional[requests.Session] = None,
        access_token_provider: Optional[Callable[[], Optional[str]]] = None,
    ) -> None:
        if endpoint != DEFAULT_ENDPOINT:
            raise ValueError("Only the official Binance MCP endpoint is permitted")
        self.endpoint = endpoint
        self.timeout = timeout
        self.session = session or requests.Session()
        self.access_token_provider = access_token_provider
        self._session_id: Optional[str] = None
        self._request_id = 0
        self._initialized = False

    def _headers(self) -> Dict[str, str]:
        headers = {
            "Accept": "application/json, text/event-stream",
            "Content-Type": "application/json",
            "User-Agent": "crypto-ai-trader-binance-readonly-poc/1.0",
        }
        if self._session_id:
            headers["Mcp-Session-Id"] = self._session_id
        if self.access_token_provider:
            access_token = self.access_token_provider()
            if access_token:
                headers["Authorization"] = f"Bearer {access_token}"
        return headers

    def _decode_response(self, response: requests.Response) -> Dict[str, Any]:
        try:
            response.raise_for_status()
        except requests.HTTPError as exc:
            if response.status_code == 401:
                raise MCPError(
                    "Binance MCP OAuth authorization is missing, expired, or rejected"
                ) from exc
            raise MCPError(f"Binance MCP HTTP {response.status_code}") from exc
        content_type = response.headers.get("Content-Type", "").lower()
        if "text/event-stream" in content_type:
            events = []
            for line in response.text.splitlines():
                if line.startswith("data:"):
                    payload = line[5:].strip()
                    if payload and payload != "[DONE]":
                        events.append(json.loads(payload))
            if not events:
                raise MCPError("MCP server returned an empty event stream")
            data = events[-1]
        else:
            data = response.json()
        if not isinstance(data, dict):
            raise MCPError("MCP response must be a JSON object")
        if data.get("error"):
            raise MCPError(f"MCP error: {data['error']}")
        return data

    def _post(self, payload: Mapping[str, Any]) -> Dict[str, Any]:
        started = time.monotonic()
        response = self.session.post(
            self.endpoint,
            headers=self._headers(),
            json=dict(payload),
            timeout=self.timeout,
        )
        session_id = response.headers.get("Mcp-Session-Id")
        if session_id:
            self._session_id = session_id
        data = self._decode_response(response)
        logger.info(
            "binance_mcp request_id=%s method=%s latency_ms=%d status=%s params=%s",
            payload.get("id"),
            payload.get("method"),
            int((time.monotonic() - started) * 1000),
            response.status_code,
            redact(payload.get("params", {})),
        )
        return data

    def _notify(self, method: str) -> None:
        """Send an MCP notification; successful notifications may have no body."""
        response = self.session.post(
            self.endpoint,
            headers=self._headers(),
            json={"jsonrpc": "2.0", "method": method},
            timeout=self.timeout,
        )
        try:
            response.raise_for_status()
        except requests.HTTPError as exc:
            raise MCPError(f"Binance MCP notification HTTP {response.status_code}") from exc
        session_id = response.headers.get("Mcp-Session-Id")
        if session_id:
            self._session_id = session_id
        logger.info("binance_mcp notification=%s status=%s", method, response.status_code)

    def _request(self, method: str, params: Optional[Mapping[str, Any]] = None) -> Any:
        self._request_id += 1
        data = self._post(
            {
                "jsonrpc": "2.0",
                "id": self._request_id,
                "method": method,
                "params": dict(params or {}),
            }
        )
        return data.get("result")

    def initialize(self) -> Mapping[str, Any]:
        if self._initialized:
            return {}
        result = self._request(
            "initialize",
            {
                "protocolVersion": PROTOCOL_VERSION,
                "capabilities": {},
                "clientInfo": {
                    "name": "crypto-ai-trader-readonly-poc",
                    "version": "1.0.0",
                },
            },
        )
        # MCP initialized is a notification and therefore has no id.
        self._notify("notifications/initialized")
        self._initialized = True
        return result or {}

    @staticmethod
    def _classify_tool(tool: Mapping[str, Any]) -> tuple[bool, str]:
        name = str(tool.get("name", ""))
        description = str(tool.get("description", ""))
        combined = f"{name} {description}"
        annotations = tool.get("annotations") or {}

        if annotations.get("readOnlyHint") is not True:
            return False, "missing MCP readOnlyHint=true"
        if _WRITE_OR_PRIVATE_TERMS.search(combined):
            return False, "name/description contains private or write capability"
        if not _MARKET_TERMS.search(combined):
            return False, "not recognizably public market data"
        return True, "MCP read-only annotation and public-market policy matched"

    def inventory(self) -> List[ToolInventoryItem]:
        self.initialize()
        result = self._request("tools/list") or {}
        tools = result.get("tools", []) if isinstance(result, Mapping) else []
        inventory: List[ToolInventoryItem] = []
        for tool in tools:
            eligible, reason = self._classify_tool(tool)
            inventory.append(
                ToolInventoryItem(
                    name=str(tool.get("name", "")),
                    description=str(tool.get("description", "")),
                    input_schema=tool.get("inputSchema") or {},
                    annotations=tool.get("annotations") or {},
                    read_only_eligible=eligible,
                    policy_reason=reason,
                )
            )
        return inventory

    def call_read_only(self, tool_name: str, arguments: Mapping[str, Any]) -> Any:
        inventory = {item.name: item for item in self.inventory()}
        tool = inventory.get(tool_name)
        if tool is None:
            raise ReadOnlyPolicyError(f"Unknown MCP tool: {tool_name}")
        if not tool.read_only_eligible:
            raise ReadOnlyPolicyError(
                f"Tool is blocked by the public-market policy: {tool.policy_reason}"
            )
        if contains_sensitive_key(arguments):
            raise ReadOnlyPolicyError("Credential-like arguments are not permitted")

        call_id = str(uuid.uuid4())
        logger.info(
            "binance_mcp_call call_id=%s tool=%s args=%s source=agent.binance.com",
            call_id,
            tool_name,
            redact(arguments),
        )
        return self._request(
            "tools/call", {"name": tool_name, "arguments": dict(arguments)}
        )

    def call_account_read_only(
        self,
        tool_name: str,
        arguments: Mapping[str, Any],
        allowed_tools: Iterable[str],
    ) -> Any:
        """Call an explicitly allowlisted account-read tool.

        This is intentionally separate from the public-market policy. Visibility in
        the OAuth inventory is not sufficient: the caller must provide an exact
        configured allowlist, and the MCP tool must declare readOnlyHint=true.
        """
        allowed = set(allowed_tools)
        if tool_name not in allowed:
            raise ReadOnlyPolicyError("Account tool is not explicitly allowlisted")
        inventory = {item.name: item for item in self.inventory()}
        tool = inventory.get(tool_name)
        if tool is None:
            raise ReadOnlyPolicyError(f"Unknown MCP tool: {tool_name}")
        combined = f"{tool.name} {tool.description}"
        if tool.annotations.get("readOnlyHint") is not True:
            raise ReadOnlyPolicyError("Account tool is missing MCP readOnlyHint=true")
        if _WRITE_TERMS.search(combined):
            raise ReadOnlyPolicyError("Account tool contains write capability")
        if contains_sensitive_key(arguments):
            raise ReadOnlyPolicyError("Credential-like arguments are not permitted")
        logger.info(
            "binance_mcp_account_read tool=%s args=%s source=agent.binance.com",
            tool_name,
            redact(arguments),
        )
        return self._request(
            "tools/call", {"name": tool_name, "arguments": dict(arguments)}
        )
