"""
Coinbase exchange implementation
"""
import ccxt.async_support as ccxt
import asyncio
from .base_exchange import BaseExchange
from loguru import logger


class CoinbaseExchange(BaseExchange):
    """Coinbase exchange implementation"""
    
    def __init__(self):
        """Initialize the Coinbase exchange"""
        super().__init__("coinbase")
        self.exchange = ccxt.coinbase({
            'enableRateLimit': True,
            'timeout': 10000,  # 10 second timeout
        })
    
    async def fetch_orderbook(self, symbol):
        """
        Fetch orderbook for a symbol from Coinbase
        
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
            
            # Coinbase Pro uses different symbol format (without slashes)
            coinbase_symbol = symbol.replace("/", "-")
            
            # Check if the symbol exists, otherwise try to find a similar one
            if coinbase_symbol not in self.exchange.markets:
                # Try to find a similar symbol
                found = False
                for market_symbol in self.exchange.markets:
                    # Check if both symbols contain the same base and quote currencies
                    if (symbol.split("/")[0] in market_symbol and 
                        symbol.split("/")[1] in market_symbol):
                        coinbase_symbol = market_symbol
                        found = True
                        break
                if not found:
                    raise ValueError(f"Symbol {symbol} not available on Coinbase")
            
            # Fetch orderbook with limit to reduce data size
            orderbook = await self.exchange.fetch_order_book(coinbase_symbol, limit=50)
            return orderbook
        except ccxt.NetworkError as e:
            logger.error(f"Coinbase network error for {symbol}: {str(e)}")
            raise Exception(f"Coinbase network error: {str(e)}")
        except ccxt.ExchangeError as e:
            logger.error(f"Coinbase exchange error for {symbol}: {str(e)}")
            raise Exception(f"Coinbase exchange error: {str(e)}")
        except ValueError as e:
            logger.error(f"Coinbase value error for {symbol}: {str(e)}")
            raise Exception(f"Coinbase value error: {str(e)}")
        except Exception as e:
            logger.error(f"Coinbase unexpected error for {symbol}: {str(e)}")
            raise Exception(f"Coinbase unexpected error: {str(e)}")
    
    async def close(self):
        """Close exchange connection"""
        try:
            await self.exchange.close()
        except Exception as e:
            logger.error(f"Error closing Coinbase connection: {str(e)}")