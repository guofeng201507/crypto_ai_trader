# Qwen Agent — Python 自动化加密货币交易规范

> 目的：为使用 Qwen/Claude 类大模型驱动的 AI agent 编写 Python 自动交易程序提供一套工程、风控、合规和测试规范。重点覆盖现货与合约的自动化下单、跨交易所低流动性代币套利、回测与仿真、监控与审计。

---

## 1. 适用范围
- 语言：Python（3.9+）
- 适配对象：集中化交易所（CEX）与去中心化交易所（DEX）API
- 交易策略：市价/限价下单、做市、三角/跨所套利、资金费率对冲
- 不包含：任何形式的市场操纵、洗盘、DDoS、欺诈或规避监管的做法

## 2. 安全与合规（必须遵守）
1. **遵守交易所规则**：在调用前加载并验证目标交易所的 API 使用条款与限制（速率、合约大小、KYC 要求）。
2. **权限最小化**：用于自动交易的 API key 应只授予所需权限（通常仅交易/订单权限，不包括提币权限；若需要提币，则单独隔离并多签）。
3. **风控开关**：实现全局与策略级“杀死开关（kill-switch）”，可在监测到异常时立即停止所有自动下单。
4. **资金隔离**：测试与生产资金必须严格隔离；任何模拟或回测不得用生产仓位。
5. **审计日志**：记录所有决策输入（agent prompt、市场快照、模型输出）、签名时间戳、以及最终交易指令。
6. **人机交互边界**：对高风险操作（大额下单、提币、杠杆调整）要求人工二次确认或多签审批。

## 3. 总体架构（参考）
```
+----------------------------+
|  Orchestration / Scheduler |
+----------------------------+
           |
           v
+----------------+   +-----------------+   +----------------+
| Market Fetcher |-->|  Agent / LLM    |-->|  Risk Engine   |
+----------------+   +-----------------+   +----------------+
           |                 |                    |
           v                 v                    v
     Market DB / Cache   Decision Queue     Execution Adapter
                                   |                    |
                                   v                    v
                             Exchange Adapters     Audit Log
```

### 关键模块说明
- **Market Fetcher**：聚合多个交易所的深度、逐笔（tape）/逐档（orderbook）数据，保证时序一致性与统一时间戳（UTC）。
- **Market DB / Cache**：使用时序数据库（例如 ClickHouse / TimescaleDB / Influx）存储分钟级与逐笔市场数据，保留至少 N 个月的交易与回测样本。
- **Agent / LLM**：负责策略生成与解释（可选），但所有最终下单动作必须由确定性模块（Risk Engine）进行校验。
- **Risk Engine**：执行头寸限额、滑点估计、最大可承受损失、速率限制、防止重复下单等规则。
- **Execution Adapter**：封装各交易所 API（REST & WebSocket），实现重试、退避（exponential backoff）与幂等性（idempotency）处理。
- **Audit Log & Monitoring**：Prometheus + Grafana 指标 + alert（邮件/Slack/Telegram）

## 4. Agent 行为与职责边界
- **LLM 仅用于**：生成策略候选、解释异常、撰写交易理由、生成回测参数集。
- **LLM 不直接下单**：模型输出必须转为结构化指令（JSON schema），并通过 deterministic risk engine 校验后才能执行。
- **Prompt 设计原则**：短、明确、结构化。务必在 prompt 中包含允许的最大下单额、滑点容忍度、有效时长（TTL）。

示例模型输出 schema：
```json
{
  "strategy_id": "arb_cross_01",
  "intent": "place_orders",
  "orders": [
    {"exchange":"EXA","side":"buy","symbol":"AAA/USDT","price":0.1234,"amount":100},
    {"exchange":"EXB","side":"sell","symbol":"AAA/USDT","price":0.1300,"amount":100}
  ],
  "metadata": {"expected_profit":2.1, "slippage_est":0.5}
}
```

## 5. 风控与下单验证（必须实现）
1. **幂等性检测**：基于 client_order_id 或本地生成的 request id 确保重复请求不会重复成交。
2. **最大下单原则**：不超过账户总资金的 X%（默认 1%）或单笔最大值阈（配置项）。
3. **滑点/成交概率估计**：在低流动性代币尤其必要，使用市场深度模拟（模拟吃单到目标成交量）来估计成交价格与概率。
4. **速率与失败策略**：若下单未在 T 秒内确认，则尝试取消并回滚。失败或部分成交时触发补单/对冲策略。
5. **交易暂停条件**：价格波动 > Y%/分钟、订单簿深度异常、连接断开超过阈值，均触发暂停并报警。

## 6. 回测与仿真规范
- **数据质量**：回测需使用逐笔/逐档数据，模拟交易时要考虑手续费、滑点、撮合规则与结算时间。
- **仿真模式**：支持“无风险仿真”（all dry-run）和“半真模拟”（真实下单但设置只模拟成交）两种模式。
- **指标**：回撤（max drawdown）、Sharpe、Sortino、胜率、平均收益/交易、滑点消耗、手续费消耗。
- **回放一致性**：回测结果需可复现：记录随机种子、版本号、回测时间段与数据快照哈希。

## 7. 监控与告警
- **实时指标**：账户权益、未实现盈亏、持仓量、逐分/逐秒成交量、订单簿深度、连接健康度。
- **告警阈值**：权益下降超过 X%、单笔滑点超过 Y%、API 错误率 > Z。
- **告警通路**：邮件、Webhook、Slack/企业微信、Telegram。关键告警必须有人接收并手动确认。

## 8. 日志与审计
- 每一笔由 agent 决策到最终成交的完整链路必须有可追溯日志：`[timestamp][request_id][agent_prompt][model_output][risk_decision][exchange_response]`。
- 日志保留期：生产日志至少保留 1 年（或根据合规要求），敏感信息（API key）不得明文入日志。

## 9. 测试矩阵（必做）
- 单元测试：Market adapter、order serializer、risk checks。
- 集成测试：mock 交易所（返回延迟、部分成交、拒单等场景）。
- 回测验真：在历史逐笔数据上跑 N 次不同参数组合，并检查回放一致性。
- 演练：定期演练 kill-switch、灾难恢复、以及大市场行情下的行为。

## 10. 部署与运维
- 容器化（Docker）部署，使用 k8s or Fargate 做弹性伸缩。
- Secrets 管理：使用 Vault 或云厂商 Secrets Manager，不在代码/日志中硬编码密钥。
- 熔断与隔离：每个策略/agent 运行在独立进程或容器，单个策略异常不影响整体系统。

## 11. 代码风格与工程规范
- 使用 type hints，遵循 PEP8，强制 static typing 检查（mypy），并通过 pre-commit hooks（black, isort, flake8）。
- 每个策略必须包含 `README.md`（策略说明、参数含义、风险点、回测报告链接）。
- 配置项以 YAML/JSON 存储，禁止在代码中写死敏感阈值。

## 12. 模板：最小可用 agent 交互流程（伪代码）
```py
# 1. fetch market snapshot
snapshot = market_fetcher.get_snapshot([("EXA","AAA/USDT"), ("EXB","AAA/USDT")])
# 2. build prompt & call LLM for candidate orders
prompt = build_prompt(snapshot, constraints)
model_out = qwen_client.run(prompt)
# 3. parse into structured orders
orders = parse_model_output(model_out)
# 4. risk checks
orders = risk_engine.validate(orders, account_state)
# 5. execute
execution_report = executor.place_batch(orders)
# 6. log
audit_logger.record(request_id, prompt, model_out, orders, execution_report)
```

## 13. 配置示例（YAML）
```yaml
agent:
  name: cross-exchange-arb
  max_notional_pct: 0.01  # 单次下单不超过总资产 1%
  max_order_value: 1000   # 单笔不超过 1000 USDT
  slippage_tolerance_pct: 0.5
  kill_switch_on_drawdown_pct: 5.0
exchanges:
  - name: EXA
    api_endpoint: https://api.exa.com
  - name: EXB
    api_endpoint: https://api.exb.com
```

## 14. 常见风险警示（务必阅读）
- **低流动性代币套利风险大**：极端滑点、交易对断裂、定价错误或交易所延迟都可能导致快速爆仓或锁仓。
- **合规风险**：部分交易所/代币可能存在合规问题（受制裁、被列黑名单）。上线前必须做合规筛查。
- **市场操纵**：不得实施或配合任何形式的操纵市场行为。

---

## 附录：快速检查表（上线前）
- [ ] API keys 权限检查（无提币或提币受限并有审批）
- [ ] 回测结果与仿真结果一致性校验
- [ ] 风控阈值与 kill-switch 已配置并可远程触发
- [ ] 审计日志与监控告警已接入运维值班系统
- [ ] 人工审批流程对大额/高风险操作生效

---

> 版本：1.0 — 说明：本规范为工程与风控指导模板，请根据贵司合规与法律团队进一步定制。

