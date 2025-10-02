# Qlib Crypto Trading

A cryptocurrency trading system built using Qlib, Microsoft's quantitative research platform. This module focuses on leveraging Qlib's powerful machine learning capabilities for cryptocurrency trading strategies, including data processing, feature engineering, model training, and backtesting.

## Features

- Integration with Qlib's Quant Research Framework for crypto trading
- Pre-built pipelines for crypto data processing and feature engineering
- Multiple ML models adapted for cryptocurrency markets
- Backtesting framework with realistic trading simulation
- Risk management and portfolio optimization tools
- Support for multiple cryptocurrency exchanges
- Customizable trading strategies based on Qlib's alpha research

## Project Structure

```
qlib_crypto_trading/
├── config/                    # Configuration files for Qlib and trading strategies
├── data/                      # Crypto data storage and Qlib dataset directory
├── models/                    # Trained models and model configurations
├── scripts/                   # Data processing and model training scripts
├── examples/                  # Example trading strategies and workflows
├── utils/                     # Utility functions specific to crypto trading
├── requirements.txt           # Python dependencies including Qlib
└── README.md                  # Project documentation
```

## Installation

1. Install Qlib and Qlib-data following the official documentation:
   ```bash
   pip install pyqlib
   ```

2. Install project dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up the data directory with crypto market data

## Configuration

The configuration is managed through YAML files in the `config/` directory:

- `qlib_config.yaml`: Qlib framework configuration
- `trading_config.yaml`: Trading strategy parameters
- `data_config.yaml`: Data source and processing configuration

## Usage

### Data Preparation
```bash
python scripts/prepare_crypto_data.py --config config/data_config.yaml
```

### Model Training
```bash
python scripts/train_model.py --config config/trading_config.yaml
```

### Backtesting
```bash
python scripts/backtest.py --config config/trading_config.yaml
```

### Live Trading (Paper/Simulated)
```bash
python scripts/run_trading.py --config config/trading_config.yaml
```

## Supported Models

- Linear models (Linear, Ridge, Lasso)
- Tree-based models (LGB, XGBoost)
- Deep learning models (Transformer, LSTM, GRU)
- Ensemble methods
- Custom alpha models for crypto markets

## Data Sources

This module supports multiple cryptocurrency data sources:

- Binance API
- Coinbase Pro API
- OKX API
- Custom data sources compatible with Qlib format

## Risk Management

- Position sizing based on volatility
- Stop-loss and take-profit mechanisms
- Portfolio diversification constraints
- Maximum drawdown limits

## Examples

Check the `examples/` directory for:

- Basic crypto trading strategy using Qlib
- Cross-validation example for crypto models
- Alpha combination and ensemble strategies
- Custom feature engineering for crypto markets

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## Disclaimer

This is a personal project for educational purposes only. Cryptocurrency trading involves substantial risk of loss. Do not risk money you cannot afford to lose. Past performance is not indicative of future results.