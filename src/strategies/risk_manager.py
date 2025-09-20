"""
Risk management module.
"""
import numpy as np
import sys
import os
from loguru import logger
from typing import Dict, Any

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.env_loader import get_env_variable


class RiskManager:
    """Manages trading risk and position sizing."""
    
    def __init__(self, initial_capital: float = 10000.0):
        """
        Initialize the risk manager.
        
        Args:
            initial_capital: Initial trading capital
        """
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.max_risk_per_trade = float(get_env_variable("MAX_RISK_PER_TRADE", "0.02"))
        self.max_position_size = float(get_env_variable("MAX_POSITION_SIZE", "0.10"))
        self.stop_loss_percent = float(get_env_variable("STOP_LOSS_PERCENT", "0.05"))
        self.take_profit_percent = float(get_env_variable("TAKE_PROFIT_PERCENT", "0.10"))
        
        logger.info(f"RiskManager initialized with capital: ${initial_capital:,.2f}")
    
    def calculate_position_size(self, symbol: str, entry_price: float, 
                              stop_loss_price: float = None) -> float:
        """
        Calculate position size based on risk management rules.
        
        Args:
            symbol: Trading symbol
            entry_price: Entry price
            stop_loss_price: Stop loss price (optional)
            
        Returns:
            Position size in units of the asset
        """
        # Calculate risk per trade in currency terms
        risk_amount = self.current_capital * self.max_risk_per_trade
        
        # If stop loss is provided, calculate position size based on risk
        if stop_loss_price:
            # Calculate distance to stop loss
            risk_per_unit = abs(entry_price - stop_loss_price)
            if risk_per_unit > 0:
                position_size = risk_amount / risk_per_unit
            else:
                # If no risk per unit, use position size limit
                position_size = self.current_capital * self.max_position_size / entry_price
        else:
            # Use position size limit
            position_size = self.current_capital * self.max_position_size / entry_price
        
        # Ensure position size doesn't exceed capital
        max_affordable = self.current_capital / entry_price
        position_size = min(position_size, max_affordable)
        
        logger.debug(f"Calculated position size for {symbol}: {position_size:.6f}")
        return position_size
    
    def calculate_stop_loss(self, entry_price: float, side: str) -> float:
        """
        Calculate stop loss price.
        
        Args:
            entry_price: Entry price
            side: Trade side ('buy' or 'sell')
            
        Returns:
            Stop loss price
        """
        if side.lower() == 'buy':
            stop_loss = entry_price * (1 - self.stop_loss_percent)
        else:  # sell
            stop_loss = entry_price * (1 + self.stop_loss_percent)
        
        logger.debug(f"Calculated stop loss: ${stop_loss:.2f} (entry: ${entry_price:.2f})")
        return stop_loss
    
    def calculate_take_profit(self, entry_price: float, side: str) -> float:
        """
        Calculate take profit price.
        
        Args:
            entry_price: Entry price
            side: Trade side ('buy' or 'sell')
            
        Returns:
            Take profit price
        """
        if side.lower() == 'buy':
            take_profit = entry_price * (1 + self.take_profit_percent)
        else:  # sell
            take_profit = entry_price * (1 - self.take_profit_percent)
        
        logger.debug(f"Calculated take profit: ${take_profit:.2f} (entry: ${entry_price:.2f})")
        return take_profit
    
    def update_capital(self, new_capital: float):
        """
        Update current capital.
        
        Args:
            new_capital: New capital amount
        """
        self.current_capital = new_capital
        logger.info(f"Capital updated to: ${new_capital:,.2f}")
    
    def get_risk_metrics(self) -> Dict[str, Any]:
        """
        Get current risk metrics.
        
        Returns:
            Dictionary with risk metrics
        """
        return {
            'current_capital': self.current_capital,
            'max_risk_per_trade': self.max_risk_per_trade,
            'max_position_size': self.max_position_size,
            'stop_loss_percent': self.stop_loss_percent,
            'take_profit_percent': self.take_profit_percent,
            'risk_amount_per_trade': self.current_capital * self.max_risk_per_trade,
            'max_position_value': self.current_capital * self.max_position_size
        }


def main():
    """Example usage of the RiskManager."""
    # Create risk manager
    risk_manager = RiskManager(initial_capital=10000.0)
    
    # Calculate position size
    entry_price = 50000.0
    stop_loss_price = 47500.0  # 5% stop loss
    position_size = risk_manager.calculate_position_size('BTC/USDT', entry_price, stop_loss_price)
    print(f"Position size: {position_size:.6f} BTC")
    
    # Calculate stop loss and take profit
    stop_loss = risk_manager.calculate_stop_loss(entry_price, 'buy')
    take_profit = risk_manager.calculate_take_profit(entry_price, 'buy')
    print(f"Stop loss: ${stop_loss:.2f}")
    print(f"Take profit: ${take_profit:.2f}")
    
    # Get risk metrics
    metrics = risk_manager.get_risk_metrics()
    print(f"Risk metrics: {metrics}")


if __name__ == "__main__":
    main()