# Scalping Bot

A high-frequency trading bot designed for cryptocurrency scalping strategies.

## Features

- **Order Book Analysis**: Monitors order book depth and imbalances for trading opportunities
- **Fast Execution**: Executes trades with minimal latency
- **Risk Management**: Implements stop-loss and take-profit mechanisms
- **Configurable Parameters**: Adjustable profit targets, stop losses, and position sizing
- **Multi-Exchange Support**: Works with Binance, OKX, and Coinbase

## Strategy

The scalping bot uses order book analysis to identify short-term trading opportunities:

1. **Entry Signals**: 
   - Detects order book imbalances (buying or selling pressure)
   - Enters positions when bid/ask volume ratios exceed thresholds
   - Places orders at optimal prices within the spread

2. **Exit Management**:
   - Takes profit at predefined targets (default 0.1%)
   - Cuts losses with stop-losses (default 0.05%)
   - Monitors market prices in real-time for exit conditions

3. **Risk Controls**:
   - Limits position size to a percentage of capital
   - Implements cooldown periods between trades
   - Uses the existing RiskManager for additional controls

## Configuration

The scalping bot parameters can be configured in `config/config.yaml`:

```yaml
scalping:
  exchange: "binance"          # Exchange to trade on
  profit_target: 0.001         # 0.1% profit target
  stop_loss: 0.0005            # 0.05% stop loss
  min_spread: 0.0001           # 0.01% minimum spread
  max_position_size: 0.01      # 1% of capital per trade
  initial_capital: 10000.0     # Starting capital
  refresh_rate: 1              # Seconds between checks
```

## Usage

Run the scalping bot using the main entry point:

```bash
# From project root directory
python src/main.py --mode scalping
```

Or run directly:

```bash
# From src directory
python scalping_bot.py
```

## How It Works

1. **Order Book Monitoring**: 
   - Fetches real-time order book data from the exchange
   - Analyzes bid/ask depth and volume distribution

2. **Signal Generation**:
   - Identifies order book imbalances (>1.5x volume ratio)
   - Calculates optimal entry points within the spread
   - Generates BUY/SELL signals based on market pressure

3. **Trade Execution**:
   - Calculates position size using risk management rules
   - Places market orders through the Trader module
   - Sets take-profit and stop-loss levels

4. **Position Management**:
   - Continuously monitors open positions
   - Exits positions when profit targets or stop losses are hit
   - Updates risk metrics after each trade

## Safety Features

- **Cooldown Periods**: Prevents over-trading with configurable time delays
- **Position Limits**: Caps position size as percentage of capital
- **Stop Losses**: Automatically cuts losing positions
- **Paper Trading Mode**: Supports simulation-only execution
- **Kill Switch**: Can be stopped gracefully with Ctrl+C

## Requirements

- Python 3.7+
- ccxt library for exchange connectivity
- pandas and numpy for data analysis
- loguru for logging

## Disclaimer

This is a high-frequency trading bot designed for educational purposes. Cryptocurrency trading involves substantial risk of loss. Do not risk money you cannot afford to lose. Past performance is not indicative of future results.