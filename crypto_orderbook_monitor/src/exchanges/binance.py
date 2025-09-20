"""
Binance exchange implementation
"""
import ccxt.async_support as ccxt
import asyncio
from .base_exchange import BaseExchange
from loguru import logger


class BinanceExchange(BaseExchange):
    """Binance exchange implementation"""
    
    def __init__(self):
        """Initialize the Binance exchange"""
        super().__init__("binance")
        self.exchange = ccxt.binance({
            'enableRateLimit': True,
            'timeout': 10000,  # 10 second timeout
        })
    
    async def fetch_orderbook(self, symbol):
        """
        Fetch orderbook for a symbol from Binance
        
        Args:
            symbol (str): Trading pair symbol
            
        Returns:
            dict: Orderbook data
            
        Raises:
            Exception: If there's an error fetching the orderbook
        """
        try:
            # Validate symbol exists
            if not self.exchange.markets:
                await self.exchange.load_markets()
            
            if symbol not in self.exchange.markets:
                raise ValueError(f"Symbol {symbol} not available on Binance")
            
            # Fetch orderbook with limit to reduce data size
            orderbook = await self.exchange.fetch_order_book(symbol, limit=50)
            return orderbook
        except ccxt.NetworkError as e:
            logger.error(f"Binance network error for {symbol}: {str(e)}")
            raise Exception(f"Binance network error: {str(e)}")
        except ccxt.ExchangeError as e:
            logger.error(f"Binance exchange error for {symbol}: {str(e)}")
            raise Exception(f"Binance exchange error: {str(e)}")
        except ValueError as e:
            logger.error(f"Binance value error for {symbol}: {str(e)}")
            raise Exception(f"Binance value error: {str(e)}")
        except Exception as e:
            logger.error(f"Binance unexpected error for {symbol}: {str(e)}")
            raise Exception(f"Binance unexpected error: {str(e)}")
    
    async def close(self):
        """Close exchange connection"""
        try:
            await self.exchange.close()
        except Exception as e:
            logger.error(f"Error closing Binance connection: {str(e)}")