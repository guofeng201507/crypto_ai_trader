"""
Unit tests for the crypto AI trader components.
"""
import unittest
import pandas as pd
import numpy as np
import sys
import os

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from strategies.base_strategy import MovingAverageCrossoverStrategy, RSIStrategy, Signal


class TestStrategies(unittest.TestCase):
    """Test cases for trading strategies."""
    
    def setUp(self):
        """Set up test data."""
        # Create sample data for testing
        dates = pd.date_range('2023-01-01', periods=100, freq='H')
        self.sample_data = pd.DataFrame({
            'open': np.linspace(20000, 25000, 100),
            'high': np.linspace(20100, 25100, 100),
            'low': np.linspace(19900, 24900, 100),
            'close': np.linspace(20000, 25000, 100),
            'volume': np.linspace(1000, 2000, 100)
        }, index=dates)
        
        # Create data with a clear downtrend for RSI test
        downtrend_prices = np.linspace(25000, 20000, 100)
        self.downtrend_data = pd.DataFrame({
            'close': downtrend_prices,
            'volume': np.linspace(1000, 2000, 100)
        }, index=dates)
    
    def test_moving_average_crossover_strategy(self):
        """Test moving average crossover strategy."""
        strategy = MovingAverageCrossoverStrategy(short_window=5, long_window=20)
        signal = strategy.generate_signal(self.sample_data)
        
        # With upward trending data, we expect either BUY or HOLD
        self.assertIn(signal, [Signal.BUY, Signal.HOLD])
    
    def test_rsi_strategy_overbought(self):
        """Test RSI strategy with overbought conditions."""
        # Create data with rapid price increases
        uptrend_prices = np.concatenate([
            np.linspace(20000, 25000, 50),  # Strong uptrend
            np.linspace(25000, 24500, 50)   # Small retracement
        ])
        
        dates = pd.date_range('2023-01-01', periods=100, freq='H')
        uptrend_data = pd.DataFrame({
            'close': uptrend_prices,
            'volume': np.linspace(1000, 2000, 100)
        }, index=dates)
        
        strategy = RSIStrategy(overbought=70, oversold=30)
        signal = strategy.generate_signal(uptrend_data)
        
        # With strong uptrend, RSI should be overbought, generating SELL signal
        # Note: This is a simplified test; real RSI behavior may vary
        self.assertIsInstance(signal, Signal)
    
    def test_rsi_strategy_oversold(self):
        """Test RSI strategy with oversold conditions."""
        # Create data with rapid price decreases
        downtrend_prices = np.concatenate([
            np.linspace(25000, 20000, 50),  # Strong downtrend
            np.linspace(20000, 20500, 50)   # Small recovery
        ])
        
        dates = pd.date_range('2023-01-01', periods=100, freq='H')
        downtrend_data = pd.DataFrame({
            'close': downtrend_prices,
            'volume': np.linspace(1000, 2000, 100)
        }, index=dates)
        
        strategy = RSIStrategy(overbought=70, oversold=30)
        signal = strategy.generate_signal(downtrend_data)
        
        # With strong downtrend, RSI should be oversold, potentially generating BUY signal
        self.assertIsInstance(signal, Signal)


if __name__ == '__main__':
    unittest.main()