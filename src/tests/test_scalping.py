"""
Test script for the scalping strategy.
"""
import sys
import os
import pandas as pd

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from strategies.scalping_strategy import ScalpingStrategy


def test_scalping_strategy():
    """Test the scalping strategy with sample data."""
    print("Testing Scalping Strategy...")
    
    # Create sample order book data with buying pressure
    sample_order_book_buy = {
        'bids': [
            [50000.0, 10.0],  # High bid volume
            [49999.0, 8.0],
            [49998.0, 6.0],
            [49997.0, 4.0],
            [49996.0, 2.0]
        ],
        'asks': [
            [50001.0, 1.0],   # Low ask volume
            [50002.0, 1.5],
            [50003.0, 2.0],
            [50004.0, 2.5],
            [50005.0, 3.0]
        ]
    }
    
    # Create sample order book data with selling pressure
    sample_order_book_sell = {
        'bids': [
            [50000.0, 1.0],   # Low bid volume
            [49999.0, 1.5],
            [49998.0, 2.0],
            [49997.0, 2.5],
            [49996.0, 3.0]
        ],
        'asks': [
            [50001.0, 10.0],  # High ask volume
            [50002.0, 8.0],
            [50003.0, 6.0],
            [50004.0, 4.0],
            [50005.0, 2.0]
        ]
    }
    
    # Create scalping strategy
    strategy = ScalpingStrategy(
        symbol="BTC/USDT",
        profit_target=0.001,  # 0.1%
        stop_loss=0.0005,     # 0.05%
        min_spread=0.0001,    # 0.01%
        order_book_depth=5
    )
    
    # Test buying opportunity
    print("\nTesting buying opportunity...")
    signal_buy = strategy.generate_signal(sample_order_book_buy, pd.Timestamp.now())
    print(f"Signal for buying pressure: {signal_buy}")
    
    # Test selling opportunity
    print("\nTesting selling opportunity...")
    signal_sell = strategy.generate_signal(sample_order_book_sell, pd.Timestamp.now())
    print(f"Signal for selling pressure: {signal_sell}")
    
    # Test position management
    print("\nTesting position management...")
    # Simulate opening a long position
    strategy._open_position('LONG', 50000.0)
    
    # Test take profit
    sample_order_book_tp = {
        'bids': [[50060.0, 5.0]],  # Price above take profit
        'asks': [[50061.0, 5.0]]
    }
    signal_tp = strategy.generate_signal(sample_order_book_tp, pd.Timestamp.now())
    print(f"Signal for take profit: {signal_tp}")
    
    # Reset and test stop loss
    strategy._open_position('LONG', 50000.0)
    sample_order_book_sl = {
        'bids': [[49970.0, 5.0]],  # Price below stop loss
        'asks': [[49971.0, 5.0]]
    }
    signal_sl = strategy.generate_signal(sample_order_book_sl, pd.Timestamp.now())
    print(f"Signal for stop loss: {signal_sl}")


if __name__ == "__main__":
    test_scalping_strategy()