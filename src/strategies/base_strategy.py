"""
Base trading strategy class and example implementations.
"""
import pandas as pd
import numpy as np
from abc import ABC, abstractmethod
from enum import Enum
from loguru import logger
from typing import Dict, Any


class Signal(Enum):
    """Trading signals."""
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"


class BaseStrategy(ABC):
    """Base class for all trading strategies."""
    
    def __init__(self, name: str):
        """
        Initialize the strategy.
        
        Args:
            name: Name of the strategy
        """
        self.name = name
        self.position = Signal.HOLD
        self.entry_price = 0.0
    
    @abstractmethod
    def generate_signal(self, data: pd.DataFrame) -> Signal:
        """
        Generate a trading signal based on the data.
        
        Args:
            data: Market data
            
        Returns:
            Trading signal
        """
        pass
    
    def update_position(self, signal: Signal, price: float):
        """
        Update the current position based on the signal.
        
        Args:
            signal: Trading signal
            price: Current price
        """
        if signal == Signal.BUY and self.position != Signal.BUY:
            self.position = Signal.BUY
            self.entry_price = price
            logger.info(f"BUY signal generated at price {price}")
        elif signal == Signal.SELL and self.position != Signal.SELL:
            self.position = Signal.SELL
            logger.info(f"SELL signal generated at price {price}")
        elif signal == Signal.HOLD:
            self.position = Signal.HOLD


class MovingAverageCrossoverStrategy(BaseStrategy):
    """Moving average crossover strategy."""
    
    def __init__(self, short_window: int = 10, long_window: int = 50):
        """
        Initialize the moving average crossover strategy.
        
        Args:
            short_window: Short window for moving average
            long_window: Long window for moving average
        """
        super().__init__("Moving Average Crossover")
        self.short_window = short_window
        self.long_window = long_window
    
    def generate_signal(self, data: pd.DataFrame) -> Signal:
        """
        Generate a trading signal based on moving average crossover.
        
        Args:
            data: Market data with 'close' column
            
        Returns:
            Trading signal
        """
        if len(data) < self.long_window:
            return Signal.HOLD
        
        # Calculate moving averages
        short_ma = data['close'].rolling(window=self.short_window).mean()
        long_ma = data['close'].rolling(window=self.long_window).mean()
        
        # Get the latest values
        short_ma_latest = short_ma.iloc[-1]
        long_ma_latest = long_ma.iloc[-1]
        short_ma_prev = short_ma.iloc[-2]
        long_ma_prev = long_ma.iloc[-2]
        
        # Generate signals
        if short_ma_prev <= long_ma_prev and short_ma_latest > long_ma_latest:
            return Signal.BUY
        elif short_ma_prev >= long_ma_prev and short_ma_latest < long_ma_latest:
            return Signal.SELL
        else:
            return Signal.HOLD


class RSIStrategy(BaseStrategy):
    """RSI-based trading strategy."""
    
    def __init__(self, overbought: int = 70, oversold: int = 30, window: int = 14):
        """
        Initialize the RSI strategy.
        
        Args:
            overbought: Overbought threshold
            oversold: Oversold threshold
            window: RSI calculation window
        """
        super().__init__("RSI Strategy")
        self.overbought = overbought
        self.oversold = oversold
        self.window = window
    
    def generate_signal(self, data: pd.DataFrame) -> Signal:
        """
        Generate a trading signal based on RSI.
        
        Args:
            data: Market data with 'close' column
            
        Returns:
            Trading signal
        """
        if len(data) < self.window:
            return Signal.HOLD
        
        # Calculate RSI
        rsi = self._calculate_rsi(data['close'])
        latest_rsi = rsi.iloc[-1]
        
        # Generate signals
        if latest_rsi < self.oversold:
            return Signal.BUY
        elif latest_rsi > self.overbought:
            return Signal.SELL
        else:
            return Signal.HOLD
    
    def _calculate_rsi(self, prices: pd.Series) -> pd.Series:
        """
        Calculate Relative Strength Index.
        
        Args:
            prices: Price series
            
        Returns:
            RSI series
        """
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=self.window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=self.window).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi


def main():
    """Example usage of the strategies."""
    # Create sample data
    dates = pd.date_range('2023-01-01', periods=100, freq='H')
    sample_data = pd.DataFrame({
        'close': np.random.rand(100) * 50000 + 20000,
        'volume': np.random.rand(100) * 1000 + 100
    }, index=dates)
    
    # Test moving average crossover strategy
    ma_strategy = MovingAverageCrossoverStrategy(short_window=5, long_window=20)
    ma_signal = ma_strategy.generate_signal(sample_data)
    print(f"Moving Average Crossover Signal: {ma_signal}")
    
    # Test RSI strategy
    rsi_strategy = RSIStrategy()
    rsi_signal = rsi_strategy.generate_signal(sample_data)
    print(f"RSI Signal: {rsi_signal}")


if __name__ == "__main__":
    main()