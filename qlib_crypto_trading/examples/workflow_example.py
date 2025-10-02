"""
Example workflow for Qlib Crypto Trading
Demonstrates the complete pipeline from data preparation to model training and backtesting
"""
import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Add the project root to the path to import modules
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from qlib_crypto_trading.scripts.prepare_crypto_data import CryptoDataProcessor, init_qlib
from qlib_crypto_trading.scripts.train_model import load_config, train_model, run_backtest, evaluate_model
from qlib_crypto_trading.utils.crypto_utils import calculate_technical_indicators, prepare_features_for_ml, calculate_portfolio_metrics
import qlib
import warnings
warnings.filterwarnings('ignore')


def main():
    """
    Main workflow function demonstrating the Qlib crypto trading pipeline
    """
    print("="*60)
    print("Qlib Crypto Trading - Example Workflow")
    print("="*60)
    
    # Step 1: Initialize Qlib
    print("\nStep 1: Initializing Qlib...")
    qlib_dir = os.path.expanduser("~/.qlib/qlib_data/cryptocurrency")
    init_qlib(qlib_dir=qlib_dir, region='crypto', freq='1min')
    print(f"Qlib initialized with data directory: {qlib_dir}")
    
    # Step 2: Data preparation
    print("\nStep 2: Preparing cryptocurrency data...")
    processor = CryptoDataProcessor()
    
    # Define a small subset for the example to run quickly
    processor.config['crypto_pairs'] = ['BTC/USDT']  # Just BTC for this example
    processor.config['exchanges'] = ['binance']      # Just Binance for this example
    processor.config['timeframe'] = '1h'             # 1-hour data
    processor.config['lookback_period'] = 30         # 30 days of data
    
    # Run data pipeline
    output_dir = os.path.join(project_root, "qlib_crypto_trading", "data", "qlib_crypto_data")
    os.makedirs(output_dir, exist_ok=True)
    
    crypto_data = processor.run_data_pipeline(output_dir)
    print(f"Data processing completed. Processed symbols: {list(crypto_data.keys())}")
    
    # Show sample of the processed data
    if crypto_data:
        symbol = list(crypto_data.keys())[0]
        print(f"\nSample data for {symbol}:")
        print(crypto_data[symbol].head())
    
    # Step 3: Feature engineering
    print("\nStep 3: Performing feature engineering...")
    if crypto_data:
        symbol = list(crypto_data.keys())[0]
        df_with_features = calculate_technical_indicators(crypto_data[symbol])
        df_ml_ready = prepare_features_for_ml(df_with_features)
        
        print(f"Feature engineering completed. Shape: {df_ml_ready.shape}")
        print(f"Features: {list(df_ml_ready.columns[:-1])}")  # All except target
        print(f"Target variable: {df_ml_ready.columns[-1]}")  # The target column
    
    # Step 4: Model training (using config from the config directory)
    print("\nStep 4: Training model...")
    config_path = os.path.join(project_root, "qlib_crypto_trading", "config", "trading_config.yaml")
    
    # Load config
    config = load_config(config_path)
    
    # Update config for this example to use a shorter time period
    config['trading']['dataset']['kwargs']['handler']['kwargs']['start_time'] = '2024-06-01'
    config['trading']['dataset']['kwargs']['handler']['kwargs']['end_time'] = '2024-09-01'
    
    # For the example, we'll skip actual training due to potential data dependencies
    # In a real scenario, you would call:
    # model, recorder = train_model(config)
    print("Model training would be performed here with actual Qlib dataset...")
    print("Note: This requires properly formatted Qlib data which may need additional setup")
    
    # Step 5: Backtesting (conceptual)
    print("\nStep 5: Backtesting concept...")
    print("In a full implementation, the trained model would be used for backtesting.")
    print("Backtesting would evaluate the model's performance on historical data.")
    
    # Step 6: Using utility functions
    print("\nStep 6: Demonstrating utility functions...")
    
    # Generate sample returns for portfolio metrics
    np.random.seed(42)  # For reproducible results
    sample_returns = pd.Series(np.random.normal(0.001, 0.02, 252))  # 252 daily returns
    
    metrics = calculate_portfolio_metrics(sample_returns)
    print("Portfolio metrics calculated from sample returns:")
    for metric, value in metrics.items():
        print(f"  {metric}: {value:.4f}")
    
    # Validate a crypto symbol
    test_symbol = "BTC/USDT"
    is_valid = validate_crypto_symbol(test_symbol)
    print(f"\nValidation result for '{test_symbol}': {is_valid}")
    
    # Get common exchanges
    exchanges = get_common_crypto_exchanges()
    print(f"\nCommon crypto exchanges supported: {exchanges[:5]}...")  # Show first 5
    
    print("\n" + "="*60)
    print("Example workflow completed!")
    print("\nNext steps:")
    print("1. Install Qlib with: pip install pyqlib")
    print("2. Download crypto data compatible with Qlib format")
    print("3. Run data preparation: python scripts/prepare_crypto_data.py")
    print("4. Train a model: python scripts/train_model.py --config config/trading_config.yaml")
    print("5. Run backtesting: python scripts/backtest.py --config config/trading_config.yaml")
    print("="*60)


def validate_crypto_symbol(symbol: str) -> bool:
    """
    Validate if a symbol is a valid crypto trading pair
    
    Args:
        symbol: Trading symbol (e.g., 'BTC/USDT')
        
    Returns:
        True if valid, False otherwise
    """
    # Basic validation: should contain a slash and have two parts
    if '/' not in symbol:
        return False
    
    parts = symbol.split('/')
    if len(parts) != 2:
        return False
    
    base, quote = parts
    
    # Basic checks for common crypto symbols
    if len(base) < 2 or len(base) > 10 or len(quote) < 2 or len(quote) > 10:
        return False
    
    # Check if both parts contain only alphanumeric characters and some common symbols
    import re
    if not re.match(r'^[A-Z0-9]+$', base) or not re.match(r'^[A-Z0-9]+$', quote):
        return False
    
    return True


def get_common_crypto_exchanges() -> list:
    """
    Get a list of common crypto exchanges supported by CCXT
    
    Returns:
        List of exchange names
    """
    exchanges = [
        'binance', 'coinbase', 'bybit', 'huobi', 'okx', 
        'kraken', 'kucoin', 'bitfinex', 'gateio', 'mexc'
    ]
    return exchanges


if __name__ == "__main__":
    main()