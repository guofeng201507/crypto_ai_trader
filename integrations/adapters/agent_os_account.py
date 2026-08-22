"""Fail-closed Agent OS adapter for authenticated account reads only."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from binance_agent_os.mcp import BinanceMCPClient
from integrations.adapters.agent_os_market_data import AgentOSToolMappingError, _content_payload
from integrations.domain import AccountBalanceSnapshot, AssetBalance


class AgentOSAccountReadAdapter:
    """Maps a verified account-balance tool onto provider-neutral DTOs.

    Trade and transfer methods are deliberately absent. A verified tool name must
    be supplied after the application's own OAuth discovery flow.
    """

    def __init__(self, client: BinanceMCPClient, tool_mapping: Mapping[str, str]):
        self.client = client
        self.tool_mapping = dict(tool_mapping)

    def _tool(self, capability: str) -> str:
        name = self.tool_mapping.get(capability)
        if not name:
            raise AgentOSToolMappingError(
                f"No verified Agent OS account tool mapped for capability: {capability}"
            )
        return name

    @staticmethod
    def _rows(data: Mapping[str, Any]) -> Sequence[Mapping[str, Any]]:
        for key in ("balances", "assets", "data", "rows"):
            value = data.get(key)
            if isinstance(value, list):
                return [row for row in value if isinstance(row, Mapping)]
        return []

    def get_balances(self, account_type: str = "spot") -> AccountBalanceSnapshot:
        capability = f"account_{account_type}_balances"
        tool_name = self._tool(capability)
        result = self.client.call_account_read_only(
            tool_name,
            {},
            allowed_tools=tuple(self.tool_mapping.values()),
        )
        data = _content_payload(result)
        balances = []
        for row in self._rows(data):
            asset = row.get("asset") or row.get("coin") or row.get("currency")
            if not asset:
                continue
            free = row.get("free", row.get("availableBalance", row.get("available", 0)))
            locked = row.get("locked", row.get("freeze", 0))
            balances.append(
                AssetBalance(asset=str(asset).upper(), free=float(free or 0), locked=float(locked or 0))
            )
        return AccountBalanceSnapshot(
            source="binance:agent-os",
            account_type=account_type,
            balances=tuple(balances),
            raw=data,
        )
