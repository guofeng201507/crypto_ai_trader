# 第一阶段实施记录

实施日期：2026-08-22

## 已完成

- 核对 Binance Agent OS 和 Binance MCP 官方文档。
- 确认官方端点为 `https://agent.binance.com/mcp/agentic`。
- 实现 Streamable HTTP MCP 客户端，支持初始化、工具发现及工具调用。
- 客户端固定使用官方端点，不支持自定义主机。
- 第一阶段不读取、不保存也不发送 OAuth Token、API Key 或账户凭证。
- 实现默认拒绝的只读策略：工具必须同时具有 MCP `readOnlyHint=true`、符合公共行情语义，并且不包含账户或写操作语义。
- 将只读网关接入 `trade_chatbot`：
  - `GET /api/binance-mcp/tools`：查看工具清单和本地策略判断。
  - `POST /api/binance-mcp/market-data`：调用通过策略校验的公共行情工具。
- 加入参数脱敏审计日志，包括工具名、脱敏参数、来源、延迟、状态和调用 ID。
- 单元测试覆盖允许规则、拒绝交易/账户工具、凭证脱敏和官方端点限制。

## 官方文档核对结果

官方文档说明：

- MCP 端点为 `https://agent.binance.com/mcp/agentic`。
- 权限分为 Market data、Account、Trade 和 Transfer。
- Market data 被描述为公开且无需认证。
- Transfer 仅限 Agentic 子账户内部钱包之间。
- 不提供提现权限。
- 订单、撤单和内部划转等非只读操作要求执行前确认。
- OAuth 过期时需要断开并重新连接。

来源：[Binance MCP Server 官方文档](https://developers.binance.com/en/docs/agent-native/mcp-server/agentic)

## 匿名实测结果

使用不包含任何账户资料或凭证的客户端执行：

1. `initialize`：成功。
2. `notifications/initialized`：成功。
3. `tools/list`：返回 HTTP 401 Unauthorized。

因此，当前端点的实际行为是：虽然市场数据工具本身被描述为无需认证，但 MCP 工具发现仍要求先建立 OAuth 授权上下文。第一阶段代码没有尝试绕过该要求，也没有请求或保存用户凭证。

## 启用本地网关

默认状态为关闭。启动 Trade Chatbot 前设置：

```bash
export BINANCE_MCP_READ_ONLY_ENABLED=true
export BINANCE_MCP_TIMEOUT_SECONDS=20
```

然后启动后端并访问：

```bash
curl http://localhost:5001/api/binance-mcp/tools
```

在尚未完成 Binance OAuth 连接的情况下，该接口会返回明确的认证错误，不会退回到交易权限或其他非官方数据源。

## 尚需用户参与的步骤

要完成真实的 MCP 行情调用，需要用户通过支持 Binance MCP OAuth 的客户端登录并授权。授权时应只选择 **Market data**，不选择 Account、Trade 或 Transfer。由于这会连接 Binance 账户并产生持久访问权限，必须由用户明确执行或在操作时确认。

OAuth 完成后还需要重新运行工具清单测试，以记录真实工具名称、输入 Schema、`readOnlyHint` 标注和实际响应；只有通过本地策略的工具才会被开放给 `trade_chatbot`。
