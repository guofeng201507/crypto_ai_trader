# Crypto AI Trader

An automated cryptocurrency trading system powered by artificial intelligence and machine learning algorithms.

## Features

- Real-time data fetching from multiple cryptocurrency exchanges
- Advanced technical analysis and feature engineering
- Machine learning models for price prediction
- Backtesting framework for strategy evaluation
- Live trading execution with risk management
- Configuration management system
- Comprehensive logging and monitoring
- **NEW: 3-Month High Price Tracker** - Monitors crypto prices dropping 20% from their 3-month highs (configurable)
- Scalping bot with order book analysis

## Project Structure

```
crypto_ai_trader/
├── config/                    # Configuration files
├── data/                      # Historical data storage
├── models/                    # Trained ML models
├── src/                       # Source code
│   ├── data/                  # Data fetching and preprocessing
│   ├── models/                # ML model implementations
│   ├── strategies/            # Trading strategies
│   └── utils/                 # Utility functions
├── crypto_orderbook_monitor/  # Orderbook monitoring component
├── crypto_price_monitor/      # 3-month high price tracker component
├── tests/                     # Unit tests
├── requirements.txt           # Python dependencies
└── README.md                  # Project documentation
```

## Installation

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Configure API keys in `config/` directory
4. Run the trader: `python src/main.py`

## New Feature: 3-Month High Price Tracker

The crypto_price_monitor component tracks cryptocurrency prices that have dropped from their historical highs:

### Features
- **Multi-Exchange Support**: Monitors prices across Binance, Coinbase, OKX, and other exchanges
- **Configurable Threshold**: Alert when prices drop configurable percentage (default 10%, can be changed) from historical highs
- **Configurable Timeframe**: Monitor highs from configurable number of days (default 180 days = 6 months)
- **Real-time Monitoring**: Continuously monitors prices at configurable intervals
- **Multiple Notifications**: Supports console, file, email, Discord, and Telegram alerts

### Usage
```bash
# Run continuous monitoring
python -m crypto_price_monitor.main --config config/price_monitor_config.yaml --mode continuous

# Run single check
python -m crypto_price_monitor.main --config config/price_monitor_config.yaml --mode single

# Check current status
python -m crypto_price_monitor.main --config config/price_monitor_config.yaml --mode status
```

### Configuration
Edit `config/price_monitor_config.yaml` to customize:
- Exchanges to monitor
- Trading pairs to track
- Drop threshold percentage (default 10%)
- Time period for historical highs (default 180 days)
- Notification methods

## Dependencies

- ccxt: Cryptocurrency exchange library
- pandas/numpy: Data analysis
- scikit-learn/tensorflow: Machine learning
- ta: Technical analysis indicators
- matplotlib/seaborn: Data visualization

## Disclaimer

This is a personal project for educational purposes only. Cryptocurrency trading involves substantial risk of loss. Do not risk money you cannot afford to lose.