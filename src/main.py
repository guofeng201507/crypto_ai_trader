#!/usr/bin/env python3
"""
Main entry point for the Crypto AI Trader application.
"""
import os
import sys
import argparse
import pandas as pd
from loguru import logger

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from data.data_fetcher import DataFetcher
from data.preprocessor import DataPreprocessor
from strategies.base_strategy import MovingAverageCrossoverStrategy, RSIStrategy
from strategies.backtester import Backtester
from strategies.trader import Trader
from strategies.risk_manager import RiskManager
from models.base_model import LSTMModel
from utils.config_manager import ConfigManager
from utils.env_loader import load_environment_variables


def run_backtest(config):
    """Run backtesting mode."""
    logger.info("Running in backtesting mode")
    
    # Initialize components
    fetcher = DataFetcher(config.get('exchanges', ['binance']))
    preprocessor = DataPreprocessor()
    backtester = Backtester(initial_capital=10000.0)
    
    # Get trading pairs
    trading_pairs = config.get('trading_pairs', ['BTC/USDT'])
    
    for pair in trading_pairs:
        logger.info(f"Backtesting {pair}")
        
        # Fetch data
        data = fetcher.fetch_ohlcv('binance', pair, '1h', 1000)
        if data.empty:
            logger.warning(f"No data fetched for {pair}")
            continue
        
        # Preprocess data
        cleaned_data = preprocessor.clean_data(data)
        processed_data = preprocessor.create_features(cleaned_data)
        
        # Create strategies
        ma_strategy = MovingAverageCrossoverStrategy(short_window=10, long_window=50)
        rsi_strategy = RSIStrategy()
        
        # Run backtest
        results = backtester.run_backtest(ma_strategy, processed_data, pair)
        logger.info(f"Backtest results for {pair}: {results['total_return_percent']:.2f}% return")
    
    logger.info("Backtesting completed")


def run_live_trading(config):
    """Run live trading mode."""
    logger.info("Running in live trading mode")
    
    # Initialize components
    trader = Trader('binance')
    risk_manager = RiskManager(initial_capital=10000.0)
    
    # Get account balance
    balance = trader.get_balance()
    logger.info(f"Account balance: {balance}")
    
    # Get trading pairs
    trading_pairs = config.get('trading_pairs', ['BTC/USDT'])
    
    for pair in trading_pairs:
        logger.info(f"Analyzing {pair} for trading opportunities")
        
        # In a real implementation, we would:
        # 1. Fetch real-time data
        # 2. Apply ML models for predictions
        # 3. Generate trading signals
        # 4. Apply risk management
        # 5. Place trades if conditions are met
        
        # For this demo, we'll just show what would happen
        logger.info(f"Would analyze {pair} and potentially place trades based on signals")
    
    logger.info("Live trading cycle completed")


def run_training(config):
    """Run model training mode."""
    logger.info("Running in training mode")
    
    # Initialize components
    fetcher = DataFetcher(config.get('exchanges', ['binance']))
    preprocessor = DataPreprocessor()
    
    # Get trading pairs
    trading_pairs = config.get('trading_pairs', ['BTC/USDT'])
    
    for pair in trading_pairs:
        logger.info(f"Training model for {pair}")
        
        # Fetch data
        data = fetcher.fetch_ohlcv('binance', pair, '1h', 1000)
        if data.empty:
            logger.warning(f"No data fetched for {pair}")
            continue
        
        # Preprocess data
        cleaned_data = preprocessor.clean_data(data)
        processed_data = preprocessor.create_features(cleaned_data)
        
        # Prepare data for training
        X, y = preprocessor.prepare_data_for_training(processed_data)
        
        # Create and train model
        model = LSTMModel(sequence_length=60, features_count=X.shape[2])
        logger.info(f"Training LSTM model with data shape: {X.shape}")
        
        # For demo purposes, we'll just run a few epochs
        # In practice, you'd want to train for more epochs
        try:
            history = model.train(X, y, epochs=2, batch_size=32)
            logger.info(f"Model trained successfully. Final loss: {history['loss'][-1]:.4f}")
        except Exception as e:
            logger.error(f"Training failed: {e}")
    
    logger.info("Training completed")


def main():
    """Main function for the Crypto AI Trader application."""
    parser = argparse.ArgumentParser(description='Crypto AI Trader')
    parser.add_argument('--mode', choices=['backtest', 'live', 'train'], 
                       default='backtest', help='Execution mode')
    parser.add_argument('--config', default='config/config.yaml', 
                       help='Configuration file path')
    
    args = parser.parse_args()
    
    # Load environment variables
    load_environment_variables()
    
    # Load configuration
    config = ConfigManager(args.config)
    
    logger.info("Starting Crypto AI Trader")
    logger.info(f"Mode: {args.mode}")
    logger.info(f"Config: {args.config}")
    
    # Run based on mode
    if args.mode == 'backtest':
        run_backtest(config)
    elif args.mode == 'live':
        run_live_trading(config)
    elif args.mode == 'train':
        run_training(config)
    
    logger.info("Crypto AI Trader finished")


if __name__ == "__main__":
    main()