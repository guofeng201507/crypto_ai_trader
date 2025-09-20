"""
Live trading execution module.
"""
import ccxt
import sys
import os
from loguru import logger
from typing import Dict, Any

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.env_loader import get_env_variable


class Trader:
    """Handles live trading execution."""
    
    def __init__(self, exchange_name: str):
        """
        Initialize the trader.
        
        Args:
            exchange_name: Name of the exchange to trade on
        """
        self.exchange_name = exchange_name
        self.exchange = None
        self._initialize_exchange()
    
    def _initialize_exchange(self):
        """Initialize connection to the exchange."""
        try:
            # Get API keys from environment variables
            api_key = get_env_variable(f"{self.exchange_name.upper()}_API_KEY")
            secret_key = get_env_variable(f"{self.exchange_name.upper()}_SECRET_KEY")
            
            if not api_key or not secret_key:
                logger.warning(f"API keys not found for {self.exchange_name}. "
                             f"Running in simulation mode.")
                return
            
            # Initialize exchange with authentication
            exchange_class = getattr(ccxt, self.exchange_name)
            self.exchange = exchange_class({
                'apiKey': api_key,
                'secret': secret_key,
                'enableRateLimit': True,
                'options': {
                    'adjustForTimeDifference': True
                }
            })
            
            # Load markets
            self.exchange.load_markets()
            logger.info(f"Initialized exchange: {self.exchange_name}")
            
        except Exception as e:
            logger.error(f"Failed to initialize exchange {self.exchange_name}: {e}")
    
    def place_order(self, symbol: str, side: str, amount: float, 
                   order_type: str = 'market', price: float = None) -> Dict[str, Any]:
        """
        Place an order on the exchange.
        
        Args:
            symbol: Trading pair symbol
            side: Order side ('buy' or 'sell')
            amount: Amount to trade
            order_type: Order type ('market' or 'limit')
            price: Price for limit orders (optional)
            
        Returns:
            Order result
        """
        # Check if we're in simulation mode
        if self.exchange is None:
            logger.info(f"SIMULATION: Placing {side} order for {amount} {symbol}")
            return {
                'id': 'simulated_order',
                'symbol': symbol,
                'side': side,
                'amount': amount,
                'price': price or 0,
                'status': 'simulated'
            }
        
        try:
            # Check trading mode
            trading_mode = get_env_variable("TRADING_MODE", "Paper")
            if trading_mode.lower() == "paper":
                logger.info(f"PAPER TRADING: Placing {side} order for {amount} {symbol}")
                return {
                    'id': 'paper_order',
                    'symbol': symbol,
                    'side': side,
                    'amount': amount,
                    'price': price or 0,
                    'status': 'paper_traded'
                }
            
            # Place real order
            if order_type == 'market':
                order = self.exchange.create_market_order(symbol, side, amount)
            else:
                order = self.exchange.create_limit_order(symbol, side, amount, price)
            
            logger.info(f"Order placed: {order}")
            return order
            
        except Exception as e:
            logger.error(f"Failed to place order: {e}")
            return {'error': str(e)}
    
    def get_balance(self, currency: str = None) -> Dict[str, Any]:
        """
        Get account balance.
        
        Args:
            currency: Specific currency to get balance for (optional)
            
        Returns:
            Balance information
        """
        # Check if we're in simulation mode
        if self.exchange is None:
            logger.info("SIMULATION: Returning simulated balance")
            return {
                'BTC': {'free': 1.0, 'used': 0.0, 'total': 1.0},
                'USDT': {'free': 50000.0, 'used': 0.0, 'total': 50000.0}
            }
        
        try:
            # Check trading mode
            trading_mode = get_env_variable("TRADING_MODE", "Paper")
            if trading_mode.lower() == "paper":
                logger.info("PAPER TRADING: Returning paper balance")
                return {
                    'BTC': {'free': 1.0, 'used': 0.0, 'total': 1.0},
                    'USDT': {'free': 50000.0, 'used': 0.0, 'total': 50000.0}
                }
            
            # Get real balance
            balance = self.exchange.fetch_balance()
            if currency:
                return balance.get(currency, {})
            return balance
            
        except Exception as e:
            logger.error(f"Failed to fetch balance: {e}")
            return {'error': str(e)}
    
    def get_positions(self) -> Dict[str, Any]:
        """
        Get current positions (for futures trading).
        
        Returns:
            Position information
        """
        try:
            if hasattr(self.exchange, 'fetch_positions'):
                positions = self.exchange.fetch_positions()
                return positions
            else:
                logger.warning(f"Exchange {self.exchange_name} does not support fetch_positions")
                return {}
        except Exception as e:
            logger.error(f"Failed to fetch positions: {e}")
            return {'error': str(e)}


def main():
    """Example usage of the Trader."""
    # Create trader instance
    trader = Trader('binance')
    
    # Get balance
    balance = trader.get_balance()
    print(f"Balance: {balance}")
    
    # Place a simulated order
    order = trader.place_order('BTC/USDT', 'buy', 0.001)
    print(f"Order result: {order}")


if __name__ == "__main__":
    main()