# BTC-Trading-Since-2020 Dataset (Paul Wei @coolish)

## Overview

This directory contains a mirror of the **BTC-Trading-Since-2020** dataset — a public, inspectable, and continuously extensible archive of a real BTC trading account on BitMEX.

**Trader**: Paul Wei (@coolish) — BitMEX 11th Anniversary Legend  
**Trading Period**: 2020-05-01 → 2026-04-17 (nearly 6 years)  
**Key Achievement**: ~52x return vs baseline (70x highlighted by BitMEX over 3 years)

## Original Repository

- **GitHub**: https://github.com/bwjoke/BTC-Trading-Since-2020
- **Live Dashboard**: https://wsnb.online

## Dataset Statistics

| Metric | Value |
|---|---|
| Total Orders | 43,214 |
| Execution Records | 173,058 rows |
| Wallet Events | 17,099 rows |
| Time Span | 2020-05-01 → 2026-04-17 |
| BTC Concentration (2024+) | ~99% |
| Starting Balance | 1.84 XBT (2020-05-01) |
| Adjusted Wealth | 96.39 XBT |
| Return Multiple | 52.4x vs baseline |
| External Deposits | 2 (both on day 1) |
| External Withdrawals | 66.00 XBT total |

## Trading Style

- **Manual, discretionary, chart-driven** BTC trading
- **Not** HFT or microstructure analysis
- Focus on: regime adaptation, position sizing, risk management, drawdown handling, long-term compounding
- **Settlement**: 98.9% XBT, 1.1% USDt

## Data Files

### Primary Ledgers

| File | Source API | Description |
|---|---|---|
| `api-v1-execution-tradeHistory.csv` | `/api/v1/execution/tradeHistory` | **Main execution ledger** — all fills, funding, settlements |
| `api-v1-order.csv` | `/api/v1/order` | Order intent, status transitions, lifecycle |
| `api-v1-user-walletHistory.csv` | `/api/v1/user/walletHistory?currency=all` | Deposits, withdrawals, funding, realized PnL, conversions |

### Terminal Snapshots

| File | Source API | Description |
|---|---|---|
| `api-v1-position.snapshot.csv` | `/api/v1/position` | Position state at export time |
| `api-v1-user-wallet.snapshot-all.csv` | `/api/v1/user/wallet?currency=all` | Wallet state at export time |
| `api-v1-user-margin.snapshot-all.csv` | `/api/v1/user/margin?currency=all` | Margin/equity state at export time |

### Reference & Metadata

| File | Source API | Description |
|---|---|---|
| `api-v1-user-walletSummary.all.csv` | `/api/v1/user/walletSummary?currency=all` | BitMEX-generated summary (cross-check) |
| `api-v1-instrument.all.csv` | `/api/v1/instrument` | Contract specs, instrument dictionary |
| `api-v1-wallet-assets.csv` | `/api/v1/wallet/assets` | Asset scale & wallet metadata |
| `manifest.json` | derived | Checksums, row counts, time ranges, build metadata |

### Derived Data

| File | Description |
|---|---|
| `derived-equity-curve.csv` | XBT-equivalent wallet curve across XBT + USDt balances |
| `cumulative-performance.png` | Performance chart visualization |

## Equity Curve Methodology

The `derived-equity-curve.csv` is intentionally simple and auditable:

1. **Tracks** XBT-equivalent wallet wealth (XBT + USDt balances)
2. **Baseline** = first funded XBT wallet balance after final deposit on day 1 (2020-05-01)
3. **Adjustments**: withdrawals added back, deposits subtracted, internal transfers neutralized
4. **Conversions**: XBT/USDt spot trades treated as internal swaps, not losses
5. **USDt Conversion**: using latest observed internal XBT/USDT rate in wallet ledger
6. **Ordering**: uses BitMEX timestamp (not transactTime) for event ordering
7. **Result**: public-friendly XBT-equivalent wealth curve

## Privacy Policy

The public dataset has been sanitized:
- ✅ **Removed**: account IDs, API secrets, profile data, IP/login data, chain tx hashes
- ✅ **Redacted**: tx hashes, order text, withdrawal addresses (for Withdrawal/Transfer types)
- ✅ **Retained**: trade execution text (helps explain fills, funding, settlements)

## How to Use This Data

### For Your crypto_ai_trader Project

1. **Training Data**: Use execution records for model training in `qlib_crypto_trading`
2. **Backtesting**: Validate strategies against real order lifecycle patterns
3. **Behavioral Analysis**: Study discretionary trading decisions across market cycles
4. **Risk Management**: Analyze position sizing and drawdown recovery patterns

### Key Considerations

- **Not suitable for**: HFT, CLOB microstructure, millisecond price prediction
- **Suitable for**: regime adaptation, risk management, position sizing analysis, long-term strategy validation
- **Timezone**: All timestamps in UTC
- **Exchange**: BitMEX (futures/perpetuals)

## Data Sources & Documentation

- **BitMEX API Explorer**: https://docs.bitmex.com/api-explorer/bitmex-api.html
- **BitMEX Swagger JSON**: https://www.bitmex.com/api/explorer/swagger.json
- **XBT vs BTC**: XBT is BitMEX's ticker for Bitcoin (see [CoinMarketCap](https://coinmarketcap.com/academy/glossary/xbt))

## Update Policy

Original repository updates daily with:
1. Pull full raw dataset from BitMEX
2. Rebuild with stable filenames and privacy rules
3. Commit new data
4. Tag as `data-YYYY-MM-DD`

## License & Attribution

This is a public dataset shared by Paul Wei (@coolish) for research and educational purposes. Please attribute appropriately when using this data.

**Original Repository**: https://github.com/bwjoke/BTC-Trading-Since-2020

---

*Last synced: 2026-02-08*
