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

## Project Structure

```
crypto_ai_trader/
├── config/           # Configuration files
├── data/             # Historical data storage
├── models/           # Trained ML models
├── src/              # Source code
│   ├── data/         # Data fetching and preprocessing
│   ├── models/       # ML model implementations
│   ├── strategies/   # Trading strategies
│   └── utils/        # Utility functions
├── tests/            # Unit tests
├── requirements.txt  # Python dependencies
└── README.md         # Project documentation
```

## Installation

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Configure API keys in `config/` directory
4. Run the trader: `python src/main.py`

## Dependencies

- ccxt: Cryptocurrency exchange library
- pandas/numpy: Data analysis
- scikit-learn/tensorflow: Machine learning
- ta: Technical analysis indicators
- matplotlib/seaborn: Data visualization

## Disclaimer

This is a personal project for educational purposes only. Cryptocurrency trading involves substantial risk of loss. Do not risk money you cannot afford to lose.