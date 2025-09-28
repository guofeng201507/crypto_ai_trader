"""
Scalping bot main execution module.
"""
import asyncio
import sys
import os
import pandas as pd
from datetime import datetime
from loguru import logger

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from strategies.scalping_strategy import ScalpingStrategy
from strategies.trader import Trader
from strategies.risk_manager import RiskManager
from utils.config_manager import ConfigManager
from utils.env_loader import load_environment_variables

# Import exchange connectors from orderbook monitor
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'crypto_orderbook_monitor'))
from src.exchanges.binance import BinanceExchange
from src.exchanges.okx import OkxExchange
from src.exchanges.coinbase import CoinbaseExchange


class ScalpingBot:
    """Main scalping bot execution class."""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """
        Initialize the scalping bot.
        
        Args:
            config_path: Path to configuration file
        """
        # Load environment variables
        load_environment_variables()
        
        # Load configuration
        self.config = ConfigManager(config_path)
        
        # Initialize components
        self.trading_pairs = self.config.get('trading_pairs', ['BTC/USDT'])
        self.exchange_name = self.config.get('scalping.exchange', 'binance')
        
        # Initialize exchange
        self.exchange = self._initialize_exchange()
        
        # Initialize strategy
        self.strategy = ScalpingStrategy(
            symbol=self.trading_pairs[0] if self.trading_pairs else "BTC/USDT",
            profit_target=float(self.config.get('scalping.profit_target', 0.001)),
            stop_loss=float(self.config.get('scalping.stop_loss', 0.0005)),
            min_spread=float(self.config.get('scalping.min_spread', 0.0001)),
            max_position_size=float(self.config.get('scalping.max_position_size', 0.01))
        )
        
        # Initialize trader and risk manager
        self.trader = Trader(self.exchange_name)
        self.risk_manager = RiskManager(
            initial_capital=float(self.config.get('scalping.initial_capital', 10000.0))
        )
        
        # Bot settings
        self.refresh_rate = int(self.config.get('scalping.refresh_rate', 1))  # seconds
        self.is_running = False
        
        logger.info("Scalping bot initialized")
        logger.info(f"Trading pair: {self.strategy.symbol}")
        logger.info(f"Exchange: {self.exchange_name}")
        logger.info(f"Refresh rate: {self.refresh_rate} seconds")
    
    def _initialize_exchange(self):
        """
        Initialize exchange connection.
        
        Returns:
            Exchange instance
        """
        try:
            if self.exchange_name == 'binance':
                return BinanceExchange()
            elif self.exchange_name == 'okx':
                return OkxExchange()
            elif self.exchange_name == 'coinbase':
                return CoinbaseExchange()
            else:
                raise ValueError(f"Unsupported exchange: {self.exchange_name}")
        except Exception as e:
            logger.error(f"Failed to initialize exchange {self.exchange_name}: {e}")
            raise
    
    async def start(self):
        """Start the scalping bot."""
        logger.info("Starting scalping bot...")
        self.is_running = True
        
        try:
            while self.is_running:
                await self._execute_trading_cycle()
                await asyncio.sleep(self.refresh_rate)
        except KeyboardInterrupt:
            logger.info("Received interrupt signal, stopping bot...")
        except Exception as e:
            logger.error(f"Error in trading cycle: {e}")
        finally:
            await self._cleanup()
    
    async def _execute_trading_cycle(self):
        """Execute one trading cycle."""
        try:
            # Fetch order book data
            order_book = await self.exchange.fetch_orderbook(self.strategy.symbol)
            
            # Generate trading signal
            current_time = pd.Timestamp.now()
            signal = self.strategy.generate_signal(order_book, current_time)
            
            # Execute trade if signal is generated
            if signal != "HOLD":
                await self._execute_trade(signal, order_book)
                
        except Exception as e:
            logger.error(f"Error in trading cycle: {e}")
    
    async def _execute_trade(self, signal, order_book):
        """
        Execute a trade based on the signal.
        
        Args:
            signal: Trading signal
            order_book: Current order book data
        """
        try:
            # Get current price
            best_bid = order_book['bids'][0][0] if order_book['bids'] else 0
            best_ask = order_book['asks'][0][0] if order_book['asks'] else 0
            current_price = (best_bid + best_ask) / 2 if best_bid and best_ask else 0
            
            if current_price <= 0:
                return
                
            # Calculate position size
            position_size = self.risk_manager.calculate_position_size(
                self.strategy.symbol, 
                current_price
            )
            
            # Limit position size based on scalping strategy
            max_size = self.risk_manager.current_capital * self.strategy.max_position_size / current_price
            position_size = min(position_size, max_size)
            
            if position_size <= 0:
                logger.warning("Calculated position size is zero or negative")
                return
            
            # Place order
            side = 'buy' if signal == "BUY" else 'sell'
            order = self.trader.place_order(
                self.strategy.symbol, 
                side, 
                position_size, 
                'market'
            )
            
            if 'error' not in order:
                logger.info(f"Placed {side} order: {position_size} {self.strategy.symbol} at market price")
                
                # Update strategy position
                current_time = pd.Timestamp.now()
                self.strategy.update_position(signal, current_price, current_time)
                
                # Update capital in risk manager
                if 'cost' in order:
                    new_capital = self.risk_manager.current_capital - order['cost']
                    self.risk_manager.update_capital(new_capital)
            else:
                logger.error(f"Failed to place order: {order['error']}")
                
        except Exception as e:
            logger.error(f"Error executing trade: {e}")
    
    async def _cleanup(self):
        """Clean up resources."""
        logger.info("Cleaning up...")
        try:
            if hasattr(self.exchange, 'close'):
                await self.exchange.close()
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
        
        logger.info("Scalping bot stopped")
    
    def stop(self):
        """Stop the scalping bot."""
        logger.info("Stopping scalping bot...")
        self.is_running = False


async def main():
    """Main function to run the scalping bot."""
    try:
        # Create and start scalping bot
        bot = ScalpingBot()
        await bot.start()
    except Exception as e:
        logger.error(f"Failed to start scalping bot: {e}")


if __name__ == "__main__":
    asyncio.run(main())