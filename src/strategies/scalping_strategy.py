"""
Scalping strategy implementation for high-frequency trading.
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional
from loguru import logger
from .base_strategy import BaseStrategy, Signal


class ScalpingStrategy(BaseStrategy):
    """Scalping strategy for high-frequency trading with small profits."""
    
    def __init__(self, 
                 symbol: str = "BTC/USDT",
                 profit_target: float = 0.001,  # 0.1% profit target
                 stop_loss: float = 0.0005,     # 0.05% stop loss
                 order_book_depth: int = 10,    # Number of order book levels to analyze
                 min_spread: float = 0.0001,    # Minimum spread to trade (0.01%)
                 max_position_size: float = 0.01):  # Max 1% of capital per trade
        """
        Initialize the scalping strategy.
        
        Args:
            symbol: Trading pair symbol
            profit_target: Target profit as percentage of entry price
            stop_loss: Stop loss as percentage of entry price
            order_book_depth: Number of order book levels to analyze
            min_spread: Minimum spread to consider for trading
            max_position_size: Maximum position size as percentage of capital
        """
        super().__init__("Scalping Strategy")
        self.symbol = symbol
        self.profit_target = profit_target
        self.stop_loss = stop_loss
        self.order_book_depth = order_book_depth
        self.min_spread = min_spread
        self.max_position_size = max_position_size
        self.current_position = None
        self.entry_price = 0.0
        self.take_profit_price = 0.0
        self.stop_loss_price = 0.0
        self.last_signal_time = None
        self.cooldown_period = 5  # Seconds between trades
        
    def generate_signal(self, order_book: Dict[str, Any], 
                       current_time: pd.Timestamp = None) -> Signal:
        """
        Generate a trading signal based on order book analysis.
        
        Args:
            order_book: Order book data with 'bids' and 'asks' lists
            current_time: Current timestamp for cooldown tracking
            
        Returns:
            Trading signal
        """
        # Check cooldown period
        if (self.last_signal_time is not None and 
            current_time is not None and 
            (current_time - self.last_signal_time).total_seconds() < self.cooldown_period):
            return Signal.HOLD
            
        # Check if we already have a position
        if self.current_position is not None:
            return self._manage_existing_position(order_book)
            
        # Analyze order book for scalping opportunities
        return self._analyze_order_book_for_entry(order_book)
    
    def _manage_existing_position(self, order_book: Dict[str, Any]) -> Signal:
        """
        Manage existing position with take profit or stop loss.
        
        Args:
            order_book: Current order book data
            
        Returns:
            Trading signal
        """
        if not order_book or 'bids' not in order_book or 'asks' not in order_book:
            return Signal.HOLD
            
        # Get current market prices
        best_bid = order_book['bids'][0][0] if order_book['bids'] else 0
        best_ask = order_book['asks'][0][0] if order_book['asks'] else 0
        current_price = (best_bid + best_ask) / 2 if best_bid and best_ask else 0
        
        if current_price <= 0:
            return Signal.HOLD
            
        # Check for take profit or stop loss
        if self.current_position == 'LONG':
            if current_price >= self.take_profit_price:
                logger.info(f"Take profit hit: Entry {self.entry_price}, Exit {current_price}")
                self._close_position()
                return Signal.SELL
            elif current_price <= self.stop_loss_price:
                logger.info(f"Stop loss hit: Entry {self.entry_price}, Exit {current_price}")
                self._close_position()
                return Signal.SELL
        elif self.current_position == 'SHORT':
            if current_price <= self.take_profit_price:
                logger.info(f"Take profit hit: Entry {self.entry_price}, Exit {current_price}")
                self._close_position()
                return Signal.BUY
            elif current_price >= self.stop_loss_price:
                logger.info(f"Stop loss hit: Entry {self.entry_price}, Exit {current_price}")
                self._close_position()
                return Signal.BUY
                
        return Signal.HOLD
    
    def _analyze_order_book_for_entry(self, order_book: Dict[str, Any]) -> Signal:
        """
        Analyze order book for entry opportunities.
        
        Args:
            order_book: Order book data
            
        Returns:
            Trading signal
        """
        if not order_book or 'bids' not in order_book or 'asks' not in order_book:
            return Signal.HOLD
            
        if len(order_book['bids']) < self.order_book_depth or len(order_book['asks']) < self.order_book_depth:
            return Signal.HOLD
            
        # Get best bid and ask prices
        best_bid = order_book['bids'][0][0]
        best_ask = order_book['asks'][0][0]
        
        if best_bid <= 0 or best_ask <= 0:
            return Signal.HOLD
            
        # Calculate spread
        spread = best_ask - best_bid
        spread_percentage = spread / best_bid
        
        # Check if spread is sufficient for scalping
        if spread_percentage < self.min_spread:
            return Signal.HOLD
            
        # Analyze order book depth imbalance
        bid_volume = sum([level[1] for level in order_book['bids'][:self.order_book_depth]])
        ask_volume = sum([level[1] for level in order_book['asks'][:self.order_book_depth]])
        
        # Look for opportunities based on order book imbalance
        if bid_volume > ask_volume * 1.5:  # Strong buying pressure
            # Place buy order just below best ask
            entry_price = best_ask - (spread * 0.1)  # 10% into the spread
            self._open_position('LONG', entry_price)
            return Signal.BUY
        elif ask_volume > bid_volume * 1.5:  # Strong selling pressure
            # Place sell order just above best bid
            entry_price = best_bid + (spread * 0.1)  # 10% into the spread
            self._open_position('SHORT', entry_price)
            return Signal.SELL
            
        return Signal.HOLD
    
    def _open_position(self, side: str, entry_price: float):
        """
        Open a new position.
        
        Args:
            side: Position side ('LONG' or 'SHORT')
            entry_price: Entry price
        """
        self.current_position = side
        self.entry_price = entry_price
        
        if side == 'LONG':
            self.take_profit_price = entry_price * (1 + self.profit_target)
            self.stop_loss_price = entry_price * (1 - self.stop_loss)
        else:  # SHORT
            self.take_profit_price = entry_price * (1 - self.profit_target)
            self.stop_loss_price = entry_price * (1 + self.stop_loss)
            
        logger.info(f"Opened {side} position at {entry_price}, TP: {self.take_profit_price}, SL: {self.stop_loss_price}")
    
    def _close_position(self):
        """Close current position."""
        self.current_position = None
        self.entry_price = 0.0
        self.take_profit_price = 0.0
        self.stop_loss_price = 0.0
    
    def update_position(self, signal: Signal, price: float, timestamp: pd.Timestamp):
        """
        Update position with timestamp for cooldown tracking.
        
        Args:
            signal: Trading signal
            price: Current price
            timestamp: Current timestamp
        """
        super().update_position(signal, price)
        self.last_signal_time = timestamp


def main():
    """Example usage of the ScalpingStrategy."""
    # Create sample order book data
    sample_order_book = {
        'bids': [
            [50000.0, 1.0],  # price, volume
            [49999.0, 2.0],
            [49998.0, 1.5]
        ],
        'asks': [
            [50001.0, 0.5],
            [50002.0, 1.2],
            [50003.0, 0.8]
        ]
    }
    
    # Create scalping strategy
    strategy = ScalpingStrategy(
        symbol="BTC/USDT",
        profit_target=0.001,  # 0.1%
        stop_loss=0.0005,     # 0.05%
        min_spread=0.0001     # 0.01%
    )
    
    # Generate signal
    signal = strategy.generate_signal(sample_order_book)
    print(f"Scalping signal: {signal}")


if __name__ == "__main__":
    main()