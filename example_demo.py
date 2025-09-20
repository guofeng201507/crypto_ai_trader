"""
Example script demonstrating the crypto AI trader system.
"""
import pandas as pd
import numpy as np
import sys
import os

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from data.data_fetcher import DataFetcher
from data.preprocessor import DataPreprocessor
from strategies.base_strategy import MovingAverageCrossoverStrategy, RSIStrategy
from strategies.backtester import Backtester
from models.base_model import LSTMModel
from utils.config_manager import ConfigManager
from utils.logger import LogManager


def demo_data_fetching():
    """Demonstrate data fetching functionality."""
    print("=== Data Fetching Demo ===")
    
    # Initialize data fetcher
    fetcher = DataFetcher(['binance'])
    
    # Get available symbols (this will show what's available on Binance)
    try:
        symbols = fetcher.get_available_symbols('binance')
        print(f"Available symbols on Binance: {len(symbols)}")
        if symbols:
            print(f"First 5 symbols: {symbols[:5]}")
        
        # Try to fetch some real data
        btc_data = fetcher.fetch_ohlcv('binance', 'BTC/USDT', '1h', 100)
        if not btc_data.empty:
            print(f"Fetched BTC/USDT data shape: {btc_data.shape}")
            return btc_data
        else:
            print("Could not fetch real data, using sample data")
    except Exception as e:
        print(f"Could not fetch real data: {e}")
    
    # Create sample data for demonstration
    dates = pd.date_range('2023-01-01', periods=100, freq='h')
    sample_data = pd.DataFrame({
        'open': np.random.rand(100) * 50000 + 20000,
        'high': np.random.rand(100) * 50000 + 20100,
        'low': np.random.rand(100) * 50000 + 19900,
        'close': np.random.rand(100) * 50000 + 20000,
        'volume': np.random.rand(100) * 1000 + 100
    }, index=dates)
    print("Using sample data for demonstration")
    return sample_data


def demo_preprocessing(data):
    """Demonstrate data preprocessing functionality."""
    print("\n=== Data Preprocessing Demo ===")
    
    preprocessor = DataPreprocessor()
    
    try:
        # Clean data
        cleaned_data = preprocessor.clean_data(data)
        print(f"Data shape after cleaning: {cleaned_data.shape}")
        
        # Create features
        data_with_features = preprocessor.create_features(cleaned_data)
        print(f"Data shape after feature creation: {data_with_features.shape}")
        print(f"Feature columns: {list(data_with_features.columns)}")
        
        return data_with_features
    except Exception as e:
        print(f"Error in preprocessing: {e}")
        # Return original data if preprocessing fails
        return data


def demo_strategies(data):
    """Demonstrate trading strategies."""
    print("\n=== Trading Strategies Demo ===")
    
    # Create strategies
    ma_strategy = MovingAverageCrossoverStrategy(short_window=10, long_window=50)
    rsi_strategy = RSIStrategy()
    
    # Generate signals
    ma_signal = ma_strategy.generate_signal(data)
    rsi_signal = rsi_strategy.generate_signal(data)
    
    print(f"Moving Average Crossover Signal: {ma_signal}")
    print(f"RSI Signal: {rsi_signal}")


def demo_backtesting(data):
    """Demonstrate backtesting functionality."""
    print("\n=== Backtesting Demo ===")
    
    # Create strategies
    ma_strategy = MovingAverageCrossoverStrategy(short_window=5, long_window=20)
    rsi_strategy = RSIStrategy()
    
    # Run backtester
    backtester = Backtester(initial_capital=10000.0)
    
    # Test single strategy
    results = backtester.run_backtest(ma_strategy, data, "BTC/USDT")
    print(f"MA Strategy Results: {results['total_return_percent']:.2f}% return")
    
    # Compare strategies
    strategies = [ma_strategy, rsi_strategy]
    comparison = backtester.compare_strategies(strategies, data, "BTC/USDT")
    print("\nStrategy Comparison:")
    print(comparison)


def demo_config_management():
    """Demonstrate configuration management."""
    print("\n=== Configuration Management Demo ===")
    
    config_manager = ConfigManager()
    project_name = config_manager.get('project_name', 'Default Project')
    exchanges = config_manager.get('exchanges', [])
    
    print(f"Project Name: {project_name}")
    print(f"Configured Exchanges: {exchanges}")


def demo_logging():
    """Demonstrate logging functionality."""
    print("\n=== Logging Demo ===")
    
    # Initialize log manager
    log_manager = LogManager()
    logger = log_manager.get_logger()
    
    # Test logging
    logger.info("This is an info message from the demo")
    logger.warning("This is a warning message from the demo")
    logger.error("This is an error message from the demo")
    
    print("Logging messages have been written to the console and log files")


def main():
    """Main demo function."""
    print("Crypto AI Trader Demo")
    print("=" * 50)
    
    # Demonstrate configuration management
    demo_config_management()
    
    # Demonstrate logging
    demo_logging()
    
    # Demonstrate data fetching
    data = demo_data_fetching()
    
    # Demonstrate preprocessing
    processed_data = demo_preprocessing(data)
    
    # Demonstrate strategies
    demo_strategies(processed_data)
    
    # Demonstrate backtesting
    demo_backtesting(processed_data)
    
    print("\n=== Demo Completed ===")
    print("All components of the Crypto AI Trader system have been demonstrated.")


if __name__ == "__main__":
    main()
