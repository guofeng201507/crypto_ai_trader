# Binance Futures Monitor

A real-time monitoring tool that tracks all USDT-margined perpetual contracts on Binance Futures and sends Telegram alerts when abnormal funding and open interest conditions are detected.

## Features

- **Comprehensive Data Collection**: Fetches mark price, index price, basis, funding rate, open interest, and multiple long/short ratios.
- **Automated Snapshots**: Runs every 5 minutes, appending data to per-symbol CSV files in `data/{symbol}.csv`.
- **Telegram Alerts**: Sends alerts when:
  - Absolute funding rate exceeds 0.1% (`|last_funding_rate| > 0.001`), AND
  - Recent OI surge detected (mean of last 3 snapshots / mean of last 10 snapshots > 2)
- **Persistent History**: Maintains open interest history for each symbol to detect short-term surges.

## Setup

### 1. Environment Configuration

Add the following to your `.env` file:

```env
TELEGRAM_BOT_TOKEN=<your_telegram_bot_token>
TELEGRAM_CHAT_ID=<your_telegram_chat_id>
```

**Creating a Telegram Bot**:
1. Open Telegram and search for `@BotFather`.
2. Send `/newbot` and follow the prompts to create a bot.
3. Copy the bot token provided by BotFather.

**Finding Your Chat ID**:
1. Send a message to your bot.
2. Visit `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`.
3. Look for `"chat":{"id":...}` in the JSON response.

### 2. Dependencies

Ensure the following packages are installed:

```bash
pip install requests loguru
```

## Data Sources

The monitor fetches data from the following Binance Futures API endpoints:

- **Exchange Info**: `/fapi/v1/exchangeInfo` - Lists all USDT perpetual contracts.
- **Premium Index**: `/fapi/v1/premiumIndex` - Mark price, index price, funding rate.
- **Open Interest**: `/fapi/v1/openInterest` - Current open interest (OI).
- **Long/Short Ratios**:
  - `/futures/data/globalLongShortAccountRatio` - Account-based ratio.
  - `/futures/data/topLongShortAccountRatio` - Top trader account ratio.
  - `/futures/data/topLongShortPositionRatio` - Top trader position ratio.
  - `/futures/data/takerlongshortRatio` - Taker buy/sell ratio.

All ratio endpoints use the 5-minute period aligned with the snapshot interval.

## Usage

Run the monitor:

```bash
python -m crypto_futures_monitor.main
```

Or:

```bash
python crypto_futures_monitor/main.py
```

The monitor runs indefinitely, executing a full cycle every 5 minutes. Press `Ctrl+C` to stop.

## Data Storage

Each symbol's data is saved to `data/{symbol}.csv` with the following columns:

- `timestamp`: Snapshot time (UTC ISO format).
- `mark_price`: Futures mark price.
- `index_price`: Spot index price.
- `basis`: Mark price - index price.
- `basis_percent`: Basis as a percentage of index price.
- `last_funding_rate`: Most recent funding rate (positive = longs pay shorts, negative = shorts pay longs).
- `oi`: Current open interest.
- `long_short_account_ratio`: Global account long/short ratio (optional).
- `top_trader_account_ls_ratio`: Top trader account long/short ratio (optional).
- `top_trader_position_ls_ratio`: Top trader position long/short ratio (optional).
- `taker_buy_sell_ratio`: Taker buy/sell ratio (optional).

## Alert Logic

An alert is triggered when **both** conditions are met:

1. **Extreme Funding Rate**: `|last_funding_rate| > 0.001` (0.1%)
2. **OI Surge**: `mean(OI_last_3) / mean(OI_last_10) > 2`

### Example Telegram Alert

```
⚠️ *潜在轧空信号*
Symbol: `BTCUSDT`
Funding rate: `0.1500%` (多头偏置)
OI(近3次均值) / OI(近10次均值): `2.35` (> 2)
当前时间(UTC): `2026-01-17T12:34:56+00:00`
```

## Customization

You can modify alert thresholds in [`futures_monitor.py`](file:///Users/fengguo/my_projs/crypto_ai_trader/crypto_futures_monitor/futures_monitor.py):

- **Funding rate threshold**: Change `0.001` in the `check_and_alert` method.
- **OI surge threshold**: Change `2.0` in the same method.
- **Snapshot interval**: Modify `SNAPSHOT_INTERVAL_SECONDS` (default: 300 seconds = 5 minutes).
- **OI history length**: Adjust `max_len` in `SymbolState.add_oi` (default: 10).

## Troubleshooting

- **No Telegram alerts**: Verify `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` in `.env`.
- **API errors**: Check Binance API status at https://www.binancestatus.com/.
- **Rate limiting**: Binance has rate limits; the monitor spreads requests across symbols. If you hit limits, consider increasing `SNAPSHOT_INTERVAL_SECONDS`.

## Disclaimer

This tool is for informational purposes only. High funding rates and OI surges can indicate potential short squeeze or liquidation cascades, but they do not guarantee market movements. Always conduct your own research and trade responsibly.
