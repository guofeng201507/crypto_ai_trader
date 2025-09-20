# Crypto Orderbook Monitor

A Python application that monitors orderbooks from multiple cryptocurrency exchanges (Binance, OKX, Coinbase) and detects price discrepancies for arbitrage opportunities.

## Features

- Real-time monitoring of orderbooks from Binance, OKX, and Coinbase
- Supports monitoring of SOL/USDT, DOT/USDT, and WIF/USDT trading pairs
- Detects price discrepancies between exchanges
- Configurable refresh rate and alert thresholds
- Detailed logging of arbitrage opportunities

## Prerequisites

- Python 3.7+
- pip (Python package installer)

## Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd crypto_orderbook_monitor
   ```

2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

## Configuration

Edit the `config.yaml` file to customize the monitoring settings:

- `exchanges`: Enable/disable exchanges
- `trading_pairs`: Trading pairs to monitor
- `refresh_rate`: How often to check prices (in seconds)
- `threshold_percentage`: Minimum price difference percentage to trigger alerts
- `log_level`: Logging level (DEBUG, INFO, WARNING, ERROR)
- `log_file`: Log file path

## Usage

Run the monitor:
```
python src/main.py
```

The program will continuously monitor the orderbooks and display arbitrage opportunities when detected.

## How It Works

1. The program connects to all enabled exchanges
2. It fetches orderbook data for all configured trading pairs
3. For each trading pair, it compares the best bid (highest buying price) and best ask (lowest selling price) across exchanges
4. When the price difference exceeds the configured threshold, it reports an arbitrage opportunity

## Supported Trading Pairs

- SOL/USDT
- DOT/USDT
- WIF/USDT

Note: WIF/USDT might have different naming on different exchanges (e.g., WIF-USDT on Coinbase)

## Supported Exchanges

- Binance
- OKX
- Coinbase

## Logging

The application logs to both console and file (`orderbook_monitor.log` by default). Log level can be configured in `config.yaml`.

## Disclaimer

This is a monitoring tool only. It does not execute trades automatically. Cryptocurrency trading involves substantial risk of loss. Do not risk money you cannot afford to lose.