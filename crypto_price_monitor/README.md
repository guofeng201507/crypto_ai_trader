# 3-Month High Crypto Price Tracker

A monitoring component that tracks cryptocurrency prices that have dropped 20% from their 3-month highs.

## Features

- **Multi-Exchange Support**: Monitors prices across Binance, Coinbase, OKX, and other exchanges
- **Historical Analysis**: Automatically fetches and analyzes 90 days of historical price data
- **Drop Detection**: Identifies when current prices drop 20% or more from 3-month highs
- **Real-time Monitoring**: Continuously monitors prices at configurable intervals
- **Multiple Notifications**: Supports console, file, email, Discord, and Telegram alerts
- **Configurable**: Highly customizable through YAML configuration

## Configuration

The tracker is configured through `config/price_monitor_config.yaml`:

```yaml
# List of exchanges to monitor
exchanges: ['binance', 'coinbase', 'okx']

# Trading pairs to monitor
trading_pairs: ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'ADA/USDT', 'DOT/USDT', 'AVAX/USDT', 'LINK/USDT']

# Drop threshold - alert when price drops this percentage from 3-month high
drop_threshold: 0.20  # 20%

# How often to check prices (in seconds)
refresh_rate: 60

# Directory for storing data
data_dir: 'data/'

# Days of historical data to fetch (90 days = 3 months)
price_history_days: 90

# Timeframe for historical data ('1d', '4h', '1h', etc.)
timeframe: '1d'

# Notification methods to use ('console', 'file', 'email', 'discord', 'telegram')
notification_methods: ['console', 'file']

# Email settings (if using email notifications)
email:
  smtp_server: 'smtp.gmail.com'  # Example for Gmail
  smtp_port: 587
  sender_email: 'your_email@gmail.com'
  sender_password: 'your_app_password'  # Use app password for Gmail
  recipients:
    - 'recipient1@example.com'
    - 'recipient2@example.com'

# Discord webhook URL (if using Discord notifications)
discord_webhook_url: ''

# Telegram settings (if using Telegram notifications)
telegram_bot_token: ''
telegram_chat_id: ''
```

## Usage

The tracker can run in different modes:

### Continuous Monitoring
```bash
python -m crypto_price_monitor.main --mode continuous
```

### Single Check
```bash
python -m crypto_price_monitor.main --mode single
```

### Current Status Check
```bash
python -m crypto_price_monitor.main --mode status
```

### With Custom Configuration
```bash
python -m crypto_price_monitor.main --config /path/to/custom/config.yaml --mode continuous
```

## How It Works

1. **Historical Data Fetching**: The system fetches 90 days of historical price data for each configured trading pair
2. **3-Month High Calculation**: It determines the highest price reached in the past 3 months
3. **Real-time Price Monitoring**: At configured intervals, it fetches current prices
4. **Drop Detection**: Compares current price with the 3-month high to detect drops of 20% or more
5. **Alerting**: Sends notifications when significant drops are detected

## Components

- `high_tracker.py`: Core logic for tracking highs and detecting drops
- `data_fetcher.py`: Handles data fetching from exchanges
- `notification_manager.py`: Manages different notification methods
- `config_manager.py`: Handles configuration loading and management
- `main.py`: Orchestrates the entire system

## Notification Methods

### Console
By default, alerts are logged to the console with detailed information.

### File
Alerts are saved to `data/price_drop_alerts.json` in JSON format.

### Email
Configure email settings in the config file to receive email alerts.

### Discord
Set the Discord webhook URL in the config file to send alerts to a Discord channel.

### Telegram
Configure bot token and chat ID to receive alerts via Telegram.

## Example Alert

```
🚨 3-Month High Alert 🚨
Exchange: binance
Symbol: BTC/USDT
Current Price: $28500.00
3-Month High: $40000.00
Drop: 28.75%
High Timestamp: 2023-06-15T10:30:00
Alert Time: 2023-09-15T14:22:30
```

## Data Storage

- Historical data is fetched on-demand and cached in memory
- Alerts are stored in `data/price_drop_alerts.json`
- Configuration is stored in `config/price_monitor_config.yaml`

## Requirements

- Python 3.7+
- CCXT library for exchange connectivity
- Pandas, NumPy for data processing
- Loguru for logging
- PyYAML for configuration management
- Requests for webhooks

Install requirements with:
```bash
pip install -r requirements.txt
```

## Rate Limits

The system respects exchange rate limits to avoid API abuse. The refresh rate should be set appropriately to comply with exchange limits.

## Security

- Store sensitive information (API keys, passwords) securely
- Use environment variables or secure vaults for sensitive data
- For email alerts, use app-specific passwords rather than account passwords

## Troubleshooting

- If you see rate limit errors, increase the refresh rate in the configuration
- If data isn't being fetched from an exchange, verify the exchange name is correct and the exchange is supported by CCXT
- Check logs for specific error messages
- Ensure your network connection allows access to exchange APIs

## Disclaimer

This is a monitoring tool only. It does not execute trades automatically. Cryptocurrency trading involves substantial risk of loss. Do not risk money you cannot afford to lose.