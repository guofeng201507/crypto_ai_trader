# Crypto AI Trader - Project Summary

## Overview
This project implements an end-to-end cryptocurrency trading and monitoring platform with AI/ML capabilities. The system includes historical data fetching and preprocessing, strategy design and backtesting, machine learning model training, risk-managed live/paper trading, specialized scalping, real-time market/news monitoring tools, a Qlib-based research module, and an interactive trade chatbot.

## Components Implemented

### 1. Core Trading Engine (`src/`)
- **Data Management**: [DataFetcher](file:///Users/fengguo/my_projs/crypto_ai_trader/src/data/data_fetcher.py) connects to cryptocurrency exchanges (e.g., Binance, Coinbase) using the CCXT library; [DataPreprocessor](file:///Users/fengguo/my_projs/crypto_ai_trader/src/data/preprocessor.py) cleans data, adds technical indicators, and creates features for ML models.
- **Trading Strategies**: [BaseStrategy](file:///Users/fengguo/my_projs/crypto_ai_trader/src/strategies/base_strategy.py) defines the common interface; concrete strategies include Moving Average Crossover and RSI.
- **Machine Learning**: [BaseModel](file:///Users/fengguo/my_projs/crypto_ai_trader/src/models/base_model.py) plus [LSTMModel](file:///Users/fengguo/my_projs/crypto_ai_trader/src/models/base_model.py#L94-L180) for sequence-based price prediction.
- **Risk & Execution**: [RiskManager](file:///Users/fengguo/my_projs/crypto_ai_trader/src/strategies/risk_manager.py) handles position sizing, stop losses, and take profits; [Trader](file:///Users/fengguo/my_projs/crypto_ai_trader/src/strategies/trader.py) executes trades via CCXT with support for simulation/paper trading.
- **Backtesting & CLI**: [Backtester](file:///Users/fengguo/my_projs/crypto_ai_trader/src/strategies/backtester.py) provides performance metrics (returns, drawdown, equity curve); [main](file:///Users/fengguo/my_projs/crypto_ai_trader/src/main.py) exposes CLI modes for backtesting, training, live trading, and scalping.

### 2. Scalping Bot (`src/scalping_bot.py`)
- **Orderbook-Based Scalping**: [ScalpingBot](file:///Users/fengguo/my_projs/crypto_ai_trader/src/scalping_bot.py) coordinates high-frequency scalping using orderbook data.
- **Orderbook Strategy**: [ScalpingStrategy](file:///Users/fengguo/my_projs/crypto_ai_trader/src/strategies/scalping_strategy.py) analyzes bid/ask spread and depth imbalance to open and manage short-lived positions with tight profit/stop targets.
- **Exchange Connectors**: Reuses exchange connectors from `crypto_orderbook_monitor/src/exchanges` to fetch live orderbooks.

### 3. Monitoring Tools
- **Price Monitor (`crypto_price_monitor/`)**: Tracks symbols that have dropped a configurable percentage from their multi-month highs and sends alerts via multiple channels.
- **News Monitor (`crypto_news_monitor/`)**: Polls the BlockBeats API (or a future real integration) for crypto news matching configured keywords, deduplicates articles, and persists results.
- **Orderbook Monitor (`crypto_orderbook_monitor/`)**: Monitors orderbooks across Binance, OKX, and Coinbase for arbitrage price discrepancies with configurable thresholds and detailed logging.

### 4. Qlib Crypto Trading Module (`qlib_crypto_trading/`)
- Integrates Microsoft's Qlib framework for more advanced quantitative research.
- Provides scripts for data preparation, model training, and backtesting using Qlib-based pipelines.
- Supports multiple ML models, portfolio-level evaluation, and more sophisticated factor research.

### 5. Trade Chatbot (`trade_chatbot/`)
- **Backend**: Flask-based API ([app](file:///Users/fengguo/my_projs/crypto_ai_trader/trade_chatbot/backend/app.py)) exposing chat, data, and MCP endpoints. Uses Qwen models, Alpha Vantage MCP, and a context engine to provide trading/market Q&A.
- **Frontend**: React-based single-page app providing a chat interface to the backend APIs.

### 6. Utilities
- **Configuration Manager**: [ConfigManager](file:///Users/fengguo/my_projs/crypto_ai_trader/src/utils/config_manager.py) for YAML-based configuration with dot-notation access.
- **Environment Loader**: [env_loader](file:///Users/fengguo/my_projs/crypto_ai_trader/src/utils/env_loader.py) for `.env`-based secrets and runtime settings.
- **Logger & Monitoring**: [logger utilities](file:///Users/fengguo/my_projs/crypto_ai_trader/src/utils/logger.py) for centralized logging and performance metric tracking.

## Features
- **End-to-end trading pipeline**: From data fetching and feature engineering to ML model training, backtesting, and live/paper trading.
- **Multiple strategies**: Moving Average Crossover, RSI, and an orderbook-driven Scalping Strategy.
- **ML-powered predictions**: LSTM-based sequence model for price prediction, with extensible BaseModel interface.
- **Risk-aware execution**: Position sizing, stop-loss/take-profit rules, and capital tracking.
- **High-frequency scalping**: Orderbook-based scalping bot using exchange-specific connectors.
- **Market monitoring**: 3‑month high price tracker, crypto news monitor, and cross-exchange orderbook discrepancy detector.
- **Configuration & logging**: Centralized YAML configuration, environment-driven parameters, and structured logging.
- **Interactive chatbot**: Web-based trade assistant integrated with market data and MCP endpoints.

## Usage

### Installation
```bash
pip install -r requirements.txt
```

### Running the Core Trader
```bash
# Backtesting mode
python src/main.py --mode backtest

# Training mode
python src/main.py --mode train

# Live trading mode (paper trading by default)
python src/main.py --mode live

# Scalping bot mode (uses orderbook connectors)
python src/main.py --mode scalping
```

### Running Monitoring Tools
```bash
# 3-month high price tracker (continuous)
python -m crypto_price_monitor.main --config config/price_monitor_config.yaml --mode continuous

# Crypto news monitor (continuous)
python -m crypto_news_monitor.main --config config/news_monitor_config.yaml --mode continuous

# Orderbook arbitrage monitor
cd crypto_orderbook_monitor
python main.py
```

### Running the Trade Chatbot
```bash
# Backend (Flask)
cd trade_chatbot/backend
python app.py

# Frontend (React)
cd ../frontend
npm install
npm start
```

## Testing
The system includes unit tests for core components and some monitoring/chatbot modules:
```bash
# Core strategies and engine
python -m pytest tests/ -v

# Orderbook monitor
cd crypto_orderbook_monitor
python -m pytest tests/ -v

# Trade chatbot backend
cd ../trade_chatbot
python -m pytest tests/ -v
```

## Configuration
- API keys and sensitive settings are stored in the `.env` file (copy `.env.example`).
- Core system configuration in `config/config.yaml`.
- Price monitor configuration in `config/price_monitor_config.yaml`.
- News monitor configuration in `config/news_monitor_config.yaml`.
- Qlib module configuration under `qlib_crypto_trading/config/`.

## Future Improvements
1. Improve ML model performance and data preprocessing (including Qlib pipelines).
2. Add more sophisticated trading strategies (e.g., multi-asset, options, portfolio-level).
3. Implement real-time trading with WebSocket-based data feeds and tighter latency handling.
4. Add more exchanges and trading pairs across all modules.
5. Implement portfolio optimization and risk-parity tools.
6. Expand monitoring and alerting (e.g., on-chain metrics, volatility regimes).
7. Unify dashboards for monitoring trading, scalping, and alerts via a single web UI.