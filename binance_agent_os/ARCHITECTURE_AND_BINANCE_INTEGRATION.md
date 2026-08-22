# 项目整体架构与 Binance 接入审计

首次审计：2026-08-22
最后更新：2026-08-23
审计范围：仓库中的 Python、YAML、JSON、Markdown 和前端配置；不包含 CSV 样本数据与第三方依赖内部代码。

## 1. 结论摘要

这个仓库目前更接近一个“加密交易实验与工具集合”，而不是已经统一分层的单体交易平台。仓库包含：

- 核心策略、回测、训练与交易执行；
- 价格监控；
- 多交易所订单簿监控；
- Binance Futures 指标监控；
- Qlib 数据准备与模型训练；
- 交易聊天机器人；
- 新闻监控；
- Coolish 离线账户/成交数据分析。

当前实际存在四种 Binance 接入方法：

1. **同步 CCXT**：OHLCV、Ticker、市场清单、余额、持仓、下单。
2. **异步 CCXT**：订单簿与市场清单。
3. **直接 Binance Futures REST API**：合约清单、资金费率、标记价格、持仓量、多空比和主动买卖比。
4. **Binance Agent OS MCP**：Codex 侧 OAuth、真实工具审计和公共行情 Shadow PoC 已完成；独立 Python/Flask 应用仍需自己的 OAuth 流程。

建议不要把所有 Binance 调用直接统一为 Agent OS。更合理的方向是：

> 先统一仓库内部的 Provider 接口和数据模型，再按场景选择 Agent OS、CCXT 或 Binance 原生 REST/WebSocket 作为适配器。

Agent OS 适合自然语言交互、低频工具调用和经用户确认的账户操作；高频订单簿、批量历史数据、模型训练和自动执行仍更适合直接 API 或 CCXT。

## 2. 当前整体架构

```text
                              ┌──────────────────────┐
                              │ 配置 / 环境变量      │
                              │ YAML + .env          │
                              └──────────┬───────────┘
                                         │
        ┌────────────────────────────────┼────────────────────────────────┐
        │                                │                                │
        v                                v                                v
┌─────────────────┐            ┌─────────────────────┐          ┌──────────────────┐
│ 核心交易系统    │            │ 独立监控工具        │          │ 研究与聊天系统   │
│ src/            │            │ price/orderbook/    │          │ qlib/chatbot/    │
│                 │            │ futures/news        │          │ coolish          │
└────────┬────────┘            └──────────┬──────────┘          └─────────┬────────┘
         │                                │                               │
         ├─ OHLCV: CCXT                   ├─ Price: CCXT                  ├─ Qlib: CCXT OHLCV
         ├─ Order book: async CCXT        ├─ Order book: async CCXT       ├─ Chat: Yahoo/Alpha Vantage
         ├─ Balance/position: CCXT        ├─ Futures metrics: REST        ├─ Binance MCP PoC
         └─ Orders: CCXT                  └─ Alerts: Telegram/etc.        └─ Coolish: local CSV
                                         │
                                         v
                              Binance / Coinbase / OKX
```

### 2.1 核心交易系统：`src/`

入口为 [`src/main.py`](../src/main.py)，提供四种运行模式：

| 模式 | 数据/执行路径 | 当前状态 |
|---|---|---|
| `backtest` | CCXT OHLCV → 预处理 → MA/RSI 策略 → 回测器 | 已有基本实现 |
| `train` | CCXT OHLCV → 特征处理 → LSTM | 已有基本实现 |
| `live` | CCXT 认证客户端 → 读取余额 | 目前只读取余额并打印待实现步骤，没有完整实盘循环 |
| `scalping` | 异步 CCXT 订单簿 → ScalpingStrategy → RiskManager → CCXT 下单 | 已连通代码路径，但需要特别谨慎验证 |

主要组件：

- [`src/data/data_fetcher.py`](../src/data/data_fetcher.py)：同步 CCXT 行情数据。
- [`src/strategies/trader.py`](../src/strategies/trader.py)：认证、余额、持仓和订单执行。
- [`src/strategies/risk_manager.py`](../src/strategies/risk_manager.py)：仓位与止盈止损计算。
- [`src/strategies/backtester.py`](../src/strategies/backtester.py)：策略回测。
- [`src/scalping_bot.py`](../src/scalping_bot.py)：组合订单簿、策略、风控和交易执行。

### 2.2 价格监控：`crypto_price_monitor/`

[`crypto_price_monitor/data_fetcher.py`](../crypto_price_monitor/data_fetcher.py) 再次实现了一套同步 CCXT DataFetcher，功能包括：

- 获取指定日期范围的 OHLCV；
- 从多个交易所批量获取 OHLCV；
- 通过 `fetch_ticker` 获取当前价格。

[`crypto_price_monitor/high_tracker.py`](../crypto_price_monitor/high_tracker.py) 基于这套数据计算 3 个月高点和回撤告警。通知层支持控制台、文件、邮件、Discord 与 Telegram。

### 2.3 订单簿监控：`crypto_orderbook_monitor/`

这是多交易所异步监控器，定义统一的 `BaseExchange.fetch_orderbook()`，并分别实现 Binance、OKX 和 Coinbase。

Binance 实现在 [`crypto_orderbook_monitor/src/exchanges/binance.py`](../crypto_orderbook_monitor/src/exchanges/binance.py)：

- `ccxt.async_support.binance`；
- `load_markets()`；
- `fetch_order_book(symbol, limit=50)`；
- 开启 CCXT 限速，超时 10 秒；
- 每轮仍是 REST 式异步请求，并非持续 WebSocket 订阅。

### 2.4 Binance Futures 监控：`crypto_futures_monitor/`

[`crypto_futures_monitor/futures_monitor.py`](../crypto_futures_monitor/futures_monitor.py) 是仓库中唯一直接调用 Binance 原生域名的生产代码，不经过 CCXT。

它每 5 分钟轮询所有 USDT 永续合约，将快照写入 CSV，并根据资金费率和持仓量变化发送 Telegram 告警。

### 2.5 Qlib 研究：`qlib_crypto_trading/`

[`qlib_crypto_trading/scripts/prepare_crypto_data.py`](../qlib_crypto_trading/scripts/prepare_crypto_data.py) 使用同步 CCXT 下载 Binance、Coinbase 等交易所的历史 OHLCV，然后转换成 Qlib 数据格式。

该模块服务于批量历史研究、模型训练与回测，不属于在线 Agent 工具调用场景。

### 2.6 Trade Chatbot：`trade_chatbot/`

聊天机器人当前的数据链路主要是：

- Yahoo Finance REST；
- Alpha Vantage REST/MCP；
- Qwen Chat Completions；
- 本地 Flask MCP wrapper。

第一阶段新增的 [`trade_chatbot/backend/api/binance_mcp.py`](../trade_chatbot/backend/api/binance_mcp.py) 已注册到 Flask，但它目前是独立 API：

- `GET /api/binance-mcp/tools`
- `POST /api/binance-mcp/market-data`

重要区别：[`trade_chatbot/backend/api/chat.py`](../trade_chatbot/backend/api/chat.py) 的主对话流程目前仍通过 Yahoo/Alpha Vantage 获取行情，**尚未自动选择或调用 Binance MCP**。

### 2.7 其他模块

- `crypto_news_monitor`：The BlockBeats 新闻源，与 Binance 市场 API 无直接关系。
- `coolish`：读取本地导出的账户、钱包、订单和成交 CSV，不调用 Binance。
- Telegram、Discord、邮件等属于通知出口，不是 Binance 数据入口。

## 3. Binance 调用完整清单

### 3.1 通过同步 CCXT 调用

| 位置 | CCXT 方法 | Binance 数据/操作 | 是否认证 | 调用特征 |
|---|---|---|---|---|
| `src/data/data_fetcher.py` | `load_markets()` | 市场/交易对清单 | 否 | 低频元数据 |
| `src/data/data_fetcher.py` | `fetch_ohlcv()` | K 线与成交量 | 否 | 回测/训练批量读取 |
| `crypto_price_monitor/data_fetcher.py` | `fetch_ohlcv()` | 历史 K 线 | 否 | 多交易所、日期范围 |
| `crypto_price_monitor/data_fetcher.py` | `fetch_ticker()` | 最新价格 | 否 | 周期性监控 |
| `qlib_crypto_trading/scripts/prepare_crypto_data.py` | `fetch_ohlcv()` | 历史 K 线 | 否 | 大批量研究数据 |
| `src/strategies/trader.py` | `load_markets()` | 市场元数据 | 是 | 创建认证客户端时调用 |
| `src/strategies/trader.py` | `fetch_balance()` | 账户余额 | 是 | 非公开账户数据 |
| `src/strategies/trader.py` | `fetch_positions()` | 合约持仓 | 是 | 非公开账户数据 |
| `src/strategies/trader.py` | `create_market_order()` | 市价单 | 是 | 资金写操作 |
| `src/strategies/trader.py` | `create_limit_order()` | 限价单 | 是 | 资金写操作 |

CCXT 会在内部转换为 Binance REST API 请求。仓库没有直接控制这些最终 URL，也没有把 CCXT 响应统一转换为项目级 DTO。

### 3.2 通过异步 CCXT 调用

| 位置 | CCXT 方法 | 用途 | 调用频率 |
|---|---|---|---|
| `crypto_orderbook_monitor/src/exchanges/binance.py` | `load_markets()` | 校验交易对 | 初始化/缓存缺失时 |
| 同上 | `fetch_order_book(limit=50)` | 50 档订单簿 | 默认每秒轮询 |
| `src/scalping_bot.py` | 间接调用上述方法 | 生成超短线信号 | 默认每秒一轮 |

虽然代码使用异步 CCXT，但当前实现不是 WebSocket 流。对每秒订单簿策略而言，这会产生延迟、请求权重和限速风险。

### 3.3 直接 Binance Futures REST API

基础域名：`https://fapi.binance.com`

| 方法 | Endpoint | 参数 | 返回用途 |
|---|---|---|---|
| `get_usdt_perpetual_symbols` | `GET /fapi/v1/exchangeInfo` | 无 | USDT 永续合约清单 |
| `fetch_premium_index` | `GET /fapi/v1/premiumIndex` | `symbol` | 标记价格、指数价格、最近资金费率 |
| `fetch_open_interest` | `GET /fapi/v1/openInterest` | `symbol` | 当前持仓量 |
| `fetch_long_short_account_ratio` | `GET /futures/data/globalLongShortAccountRatio` | `symbol, period=5m, limit=1` | 全市场账户多空比 |
| `fetch_top_trader_account_ls_ratio` | `GET /futures/data/topLongShortAccountRatio` | 同上 | 大户账户多空比 |
| `fetch_top_trader_position_ls_ratio` | `GET /futures/data/topLongShortPositionRatio` | 同上 | 大户持仓多空比 |
| `fetch_taker_buy_sell_ratio` | `GET /futures/data/takerlongshortRatio` | 同上 | 主动买卖量比 |

这些端点当前均为公开读取，无 API Key、签名或账户权限。

### 3.4 Binance Agent OS MCP

实现位置：[`binance_agent_os/mcp/client.py`](mcp/client.py)

| MCP 方法 | 用途 | 当前结果 |
|---|---|---|
| `initialize` | 协商 MCP 协议与客户端信息 | 匿名实测成功 |
| `notifications/initialized` | 完成初始化通知 | 匿名实测成功 |
| `tools/list` | 获取服务器工具清单 | 匿名实测返回 401 |
| `tools/call` | 调用通过只读策略的工具 | 等待 OAuth 和真实工具清单 |

网关当前只允许：

- 官方端点 `https://agent.binance.com/mcp/agentic`；
- 具有 `annotations.readOnlyHint=true` 的工具；
- 名称/描述明确符合公共市场数据语义的工具；
- 不含凭证形态参数的请求。

公共行情入口仍拒绝账户、订单、交易和划转语义。2026-08-23 新增了独立的账户只读边界：只有应用 OAuth 后真实发现、配置精确映射、声明 `readOnlyHint=true` 且不含写操作语义的账户工具才可调用；Trade 与 Transfer 仍未开放。

## 4. 当前重复与架构问题

### 4.1 存在三套行情 DataFetcher

- `src/data/data_fetcher.py`
- `crypto_price_monitor/data_fetcher.py`
- `qlib_crypto_trading/scripts/prepare_crypto_data.py` 内部实现

它们都直接初始化 CCXT，并各自处理 OHLCV。错误处理、分页、时间范围、返回格式、重试与缓存行为不一致。

### 4.2 交易所抽象只覆盖订单簿

`crypto_orderbook_monitor` 的 `BaseExchange` 只有 `fetch_orderbook()`。OHLCV、Ticker、Futures 指标、账户和执行没有共享接口，因此其他模块继续直接依赖 CCXT 或 `requests`。

### 4.3 同步与异步边界混杂

核心 DataFetcher 和 Trader 使用同步 CCXT；订单簿使用异步 CCXT；Futures Monitor 使用同步 Requests。没有统一超时、重试、熔断、限速预算或可观测性。

### 4.4 符号格式不统一

- CCXT 使用 `BTC/USDT`；
- Binance Futures REST 使用 `BTCUSDT`；
- Chatbot/Yahoo 使用 `BTC-USD`。

当前转换散落在不同模块中，未来替换 Provider 时容易出现错误。

### 4.5 “实时”模块实际主要依赖轮询

仓库虽然声明或依赖 WebSocket，但审计未发现 Binance WebSocket 的实际订阅实现。订单簿默认每秒轮询，Futures 指标每 5 分钟轮询。

### 4.6 Chatbot 尚未真正编排 Binance MCP

Binance MCP Flask Blueprint 已存在，但 Qwen 对话流程没有工具选择、Schema 注入、工具结果回填或来源标注流程。因此当前状态是“网关可选”，不是“聊天 Agent 已接入”。

### 4.7 实盘执行边界不够强

`Trader` 在 `TRADING_MODE` 非 `paper` 时可直接调用真实下单方法，但当前缺少统一的：

- 明确人工批准状态；
- 幂等键；
- 订单提交后对账；
- 每日亏损硬限制；
- Kill switch；
- API 权限启动检查；
- 审计事件结构。

在这些能力完成前，不应把 Agent OS 的 Trade 权限接入该执行路径。

## 5. 是否可统一使用 Agent OS

### 5.1 适合优先迁移或新增 Agent OS Adapter

| 场景 | 适合度 | 原因 |
|---|---:|---|
| Chatbot 查询 Binance 当前价格、24h 变化 | 高 | 自然语言、低频、可显示来源 |
| Chatbot 查询订单簿、K 线、资金费率 | 高/中 | 官方文档明确提及，但需核对真实工具 Schema |
| 人工发起的余额/持仓查询 | 中 | MCP 支持，但需要 OAuth 与 Account scope |
| 人工确认后的小额交易 | 中 | Agent OS 有确认机制和 Agentic 子账户隔离，但仍需本地风控 |
| 运维或研究人员临时查询市场状态 | 高 | MCP 的工具发现和自然语言能力有明显价值 |

### 5.2 不建议直接替换为 Agent OS

| 场景 | 建议 | 原因 |
|---|---|---|
| 每秒订单簿监控与 Scalping | 保留/改为原生 WebSocket | MCP 延迟、采样一致性、深度增量和吞吐保证不明确 |
| Qlib 批量历史数据下载 | 保留直接 API/CCXT | 需要分页、可复现、批量吞吐与时间范围控制 |
| 回测和模型训练数据 | 保留直接 API + 本地数据湖 | 不应依赖会变化的 Agent 工具响应 |
| Futures 全市场定时扫描 | 暂保留 REST | 当前使用的 OI 和多空比工具覆盖尚未证实 |
| 无人值守自动交易 | 暂不迁移 | Agent OS 每次写操作确认与现有自动化目标可能冲突 |
| Coinbase/OKX 数据 | 无法迁移 | Agent OS 是 Binance 专用平台 |

### 5.3 不能把“统一”理解为只保留一种远端协议

如果所有组件都强制使用 Agent OS，会产生以下问题：

- 失去多交易所能力；
- 高频和大批量任务经过不必要的 Agent/MCP 层；
- 数据响应可能不利于历史可复现；
- OAuth 会扩大运行环境中的身份与令牌管理范围；
- Agentic 子账户与现有主账户 API Key 交易语义不同；
- 当前 MCP 工具范围、限速和稳定性尚未验证。

因此应统一的是**应用内部契约**，而不是外部协议。

## 6. 推荐的目标架构

```text
策略 / 回测 / 监控 / Chatbot / Qlib
                 │
                 v
┌───────────────────────────────────────────┐
│ 项目统一 Domain Ports                     │
│ MarketDataPort                            │
│ HistoricalDataPort                        │
│ OrderBookStreamPort                       │
│ FuturesMetricsPort                        │
│ AccountReadPort                           │
│ ExecutionPort                             │
└──────────────────────┬────────────────────┘
                       │
       ┌───────────────┼────────────────┬─────────────────┐
       v               v                v                 v
 AgentOS MCP       Binance Native    CCXT Multi-Ex     Local Cache
 Adapter           REST/WebSocket    Adapter            / Data Lake
       │               │                │                 │
 对话与低频工具     高频/批量/执行      Coinbase/OKX       回测/训练
```

### 6.1 建议的统一接口

```python
class MarketDataPort:
    get_ticker(symbol)
    get_ohlcv(symbol, timeframe, start, end, limit)
    get_exchange_info()

class OrderBookStreamPort:
    subscribe_order_book(symbol, depth)

class FuturesMetricsPort:
    get_funding(symbol)
    get_open_interest(symbol)
    get_long_short_ratios(symbol, period)

class AccountReadPort:
    get_balances()
    get_positions()

class ExecutionPort:
    preview_order(order_request)
    submit_approved_order(approved_request)
    get_order(order_id)
    cancel_approved_order(order_id)
```

Agent OS、CCXT 和 Binance 原生接口分别实现这些 Port。策略与监控模块不再直接 import `ccxt` 或拼接 Binance URL。

### 6.2 统一数据模型

至少建立以下项目级 DTO：

- `CanonicalSymbol`：统一 base、quote、market type 和 Provider 格式转换；
- `TickerSnapshot`；
- `OHLCVBar`；
- `OrderBookSnapshot` / `OrderBookDelta`；
- `FundingSnapshot`；
- `OpenInterestSnapshot`；
- `BalanceSnapshot`；
- `PositionSnapshot`；
- `OrderRequest` / `OrderResult`。

每个数据对象都应包含：

- `source`；
- `exchange_timestamp`；
- `received_at`；
- `symbol`；
- `market_type`；
- `is_stale` 或可计算时效的信息；
- 原始请求追踪 ID。

## 7. 推荐迁移顺序

### 阶段 A：只统一读取接口，不替换 Provider

状态：**已完成第一轮实施。**

1. 新建 `integrations/ports/` 和统一 DTO。
2. 将三套 DataFetcher 合并到 `CCXTMarketDataAdapter`。
3. 将 Futures REST 逻辑封装为 `BinanceFuturesMetricsAdapter`。
4. 将订单簿实现封装为 `CCXTOrderBookAdapter`，随后评估 Binance WebSocket。
5. 保持现有行为，通过契约测试验证输出一致。

### 阶段 B：加入 Agent OS 只读 Adapter

状态：**已完成 Codex 侧 OAuth、工具审计、公共行情 Adapter 与首轮 Shadow 验证；独立 Flask 应用 OAuth 基础链路已实现。** 应用现支持 Authorization Code + PKCE、state 校验、授权码换 Token、进程内 Token Store、Bearer 注入、过期拒绝与主动断开。尚未配置真实应用 `client_id` 并完成端到端回调。

1. 完成只授予 Market data 的 OAuth。
2. 保存并审查真实 `tools/list` 清单。
3. 将 Agent OS 工具映射到统一 DTO，而不是直接把 MCP 原始结果传给策略。
4. 先让 Chatbot 使用 `AgentOSMarketDataAdapter`。
5. 以 shadow mode 同时请求 Agent OS 与现有 Provider，比较价格、时间戳、字段完整性和延迟。

### 阶段 C：按数据类型做决策

状态：**已完成第一轮覆盖和延时验证，持续性评估尚未完成。** 当前只有 5 次 Ticker 样本，尚不足以形成可靠的 P95、失败率和限速结论。

为每类数据记录：

- 工具/Endpoint 覆盖；
- P50/P95 延迟；
- 限速与失败率；
- 时间戳差异；
- 数据缺失率；
- 历史范围与分页能力；
- OAuth 生命周期；
- 地区与账户限制。

达到门槛后，才决定某类读取是否默认走 Agent OS。建议保留直接 API 作为回退，但回退必须显式标记数据来源，不能静默混用。

### 阶段 D：最后评估账户与执行

状态：**账户只读基础边界与应用 OAuth 基础已完成；真实账户调用和交易执行尚未开始。** 已新增 `AccountReadPort`、账户余额 DTO、`AgentOSAccountReadAdapter` 和 MCP 显式白名单策略。仓库进程不能继承 Codex Desktop OAuth，真实账户工具映射仍为空。Trade、Transfer 与 Withdrawal 保持禁用。

只有在以下条件同时满足后，才评估 Agent OS Account/Trade：

- 只读链路稳定；
- Agentic 子账户已隔离且仅投入可承受损失的资产；
- 风控网关、幂等、对账、熔断和 Kill switch 已完成；
- 每笔非只读操作都有清晰的人类确认边界；
- 已验证权限撤销与 Emergency stop；
- 完成测试网或极小额度验证。

## 8. 建议保留、替换与验证矩阵

| 当前组件 | 短期动作 | Agent OS 最终角色 |
|---|---|---|
| `src/data/data_fetcher.py` | 合并到统一 CCXT Adapter | 可作为低频读取的可选 Provider |
| `crypto_price_monitor/data_fetcher.py` | 与核心 DataFetcher 合并 | 可通过 shadow mode 评估替换 Ticker |
| Qlib 历史数据 | 保留直接数据链路 | 不作为默认 Provider |
| Orderbook Monitor | 保留，优先升级 WebSocket | 仅用于对话查询或低频快照 |
| Futures Monitor | 先封装原生 REST Adapter | 覆盖验证后选择性替换部分指标 |
| `Trader` 余额/持仓 | 先隔离 AccountReadPort | 可选 Agentic 子账户读取 |
| `Trader` 下单 | 加固 ExecutionPort | 最后评估，不直接替换 |
| Trade Chatbot | 优先接 Agent OS | Agent OS 的最佳首个消费者 |

## 9. 当前迁移执行状态

| 阶段 | 状态 | 已落地内容 | 下一门槛 |
|---|---|---|---|
| A：统一读取接口 | 已完成第一轮 | Provider-neutral DTO/Ports；共享 CCXT Market/OrderBook Adapter；Binance Futures Adapter；重复 DataFetcher 合并；符号统一 | 持续补充契约测试 |
| B：Agent OS 只读行情 | 基础实现完成 | OAuth 工具审计；真实行情映射；Ticker Adapter；Shadow Comparator；Flask PKCE OAuth 与内存 Token Store | 配置真实应用 client_id，完成端到端回调；生产级加密 Token Store |
| C：按数据类型评估 | 第一轮完成 | Spot/Futures 公共工具覆盖确认；5 次 Ticker 延时比较 | 长时间 P50/P95、失败率、限速、时间戳对齐 |
| D：账户与执行 | 账户只读基础完成 | `AccountReadPort`、余额 DTO、fail-closed Account Adapter、显式 allowlist、Bearer 注入 | 应用 OAuth 后确认真实账户工具；小额只读验证；风控完成后才考虑执行 |

此前迁移测试为 `60 passed, 1 deselected`。2026-08-23 加入应用 OAuth 后，针对 Integrations、OAuth、MCP Client 和 Flask API 的定向回归为 `28 passed`；提交前扩大到 Price Monitor、Orderbook、Strategies 与 Futures 的回归结果为 `70 passed, 1 failed`。唯一失败仍是历史 Futures 告警测试：测试样本计算出的 OI 比率约为 1.71，但生产规则和文档要求大于 2，因而测试期望告警与现行规则不一致。另有 News Monitor 旧接口测试未纳入本轮，与 Binance 迁移无关。

## 10. OAuth 后真实工具审计（已合并）

### 10.1 授权状态与边界

`binance-mcp-server` 已在 Codex Desktop 中加载，真实工具可发现和调用，用户同时启用了 Agentic 子账户相关能力。审计期间只调用了公共市场数据工具；未读取余额、持仓或订单，未调用 Trade、Transfer 或其他写工具。

Codex Desktop 管理的 OAuth 凭证只供已加载的 MCP Plugin 使用。仓库内 Flask/Python 进程不会自动继承该凭证，也不得从 Codex Token 存储复制凭证到项目 `.env`。独立应用必须实现自己的 OAuth 和安全 Token 生命周期，或通过明确授权的服务边界代理调用。

2026-08-23 已从 Binance 官方 OAuth 元数据端点验证并实现：issuer 为 `https://agent.binance.com`，授权端点为 `https://accounts.binance.com/agentic-oauth/authorize`，Token 端点为 `https://accounts.binance.com/oauth-agentic/token`，授权方式为 Authorization Code，PKCE 只支持 `S256`，Token Endpoint 客户端认证方式为 `none`。Flask 提供：

- `GET /api/binance-mcp/oauth/start`：生成 state、PKCE verifier/challenge 并跳转授权页；
- `GET /api/binance-mcp/oauth/callback`：校验 state 并交换 Access Token；
- `POST /api/binance-mcp/oauth/disconnect`：清除本进程 Token；
- MCP Client：仅通过 `Authorization: Bearer` 请求头注入有效 Token。

当前 Token Store 仅在内存中，重启即丢失，适合本地验证但不适合多进程或生产部署；Access Token 不写 YAML、`.env` 或日志。官方元数据未声明 Refresh Token grant，因此当前实现不会猜测刷新流程，Token 过期后需重新授权。

Flask OAuth state 保存在签名 Session 中。未配置 `SECRET_KEY` 时，本地进程会生成一次性高熵密钥，避免使用已知默认值；生产或多进程部署必须通过环境变量提供各进程一致的强随机 `SECRET_KEY`。

### 10.2 已确认的工具覆盖

| 项目需求 | 已验证 MCP 工具 | 实测状态 |
|---|---|---|
| Spot 最新价格 | `spot.tickerPrice` | 成功 |
| Spot 24h 行情 | `spot.ticker24hr` | 成功 |
| Spot OHLCV | `spot.klines` | 成功 |
| Spot 订单簿 | `spot.depth` | 成功 |
| USD-M 合约清单 | `futures_usds.exchangeInformation` | Schema 已确认 |
| 标记价格/资金费率 | `futures_usds.markPrice` | Schema 已确认 |
| 资金费率历史 | `futures_usds.getFundingRateHistory` | Schema 已确认 |
| 当前持仓量 | `futures_usds.openInterest` | 成功 |
| 持仓量统计 | `futures_usds.openInterestStatistics` | Schema 已确认 |
| 全市场多空比 | `futures_usds.longShortRatio` | 成功 |
| 大户账户多空比 | `futures_usds.topTraderLongShortRatioAccounts` | Schema 已确认 |
| 大户持仓多空比 | `futures_usds.topTraderLongShortRatioPositions` | Schema 已确认 |
| 主动买卖量比 | `futures_usds.takerBuySellVolume` | Schema 已确认 |

Spot 与 USD-M Futures 的项目所需公共数据均存在对应工具。账户、Trade 和资产管理工具在授权后可见，但“可见”不等于项目已允许调用。项目当前公共行情白名单只包含 `agent_os_tool_mapping.example.yaml` 中的市场数据工具；账户映射默认留空，Trade/Transfer 不提供 Adapter。

### 10.3 首轮性能结果

同一轮对 BTCUSDT 最新价格各采样 5 次：

| Provider | 延迟样本（ms） | 中位数 | 结论 |
|---|---|---:|---|
| Agent OS MCP | 3860, 2616, 2779, 3062, 4490 | 3062 ms | 适合 Chatbot、人工查询和低频工作流 |
| CCXT/Binance 公共 API | 1492.8, 80.1, 82.6, 91.2, 81.7 | 82.6 ms | 首次建连慢，连接复用后约 80–91 ms |

价格差异处于数秒市场波动范围，首个样本约差 2.83 bps，不能据此判断数据不一致。后续需尽量并发请求并按交易所时间戳对齐。Agent OS 不应作为每秒 Scalping 订单簿的默认 Provider；实时盘口优先使用 Binance 原生 WebSocket，批量历史数据继续使用直接 API/CCXT 并本地持久化。

## 11. 下一步执行顺序

1. 配置 Binance 接受的应用 `client_id` 与回调 URI，实际完成一次 Flask OAuth 回调；账户映射在此之前保持为空。
2. OAuth 后重新执行 `tools/list`，只把真实且 `readOnlyHint=true` 的余额/持仓工具填入 `account_capabilities`。
3. 使用 Agentic 子账户进行余额只读验证，并与 CCXT/原生账户查询做 Shadow 对账。
4. 生产化前将内存 Token Store 替换为加密、可撤销、支持多进程的凭证存储；不假设服务端提供 Refresh Token。
5. 延长公共行情测试，记录 P50/P95、失败率、限速和时间戳差异。
6. 实现 Binance 原生 WebSocket 数据平面，替换当前每秒 REST 订单簿轮询。
7. 在幂等、订单对账、熔断、Kill switch 和人工确认边界完成前，不迁移 Trade/Transfer。
