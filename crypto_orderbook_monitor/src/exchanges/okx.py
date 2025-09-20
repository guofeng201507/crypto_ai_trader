"""
OKX exchange implementation
"""
import ccxt.async_support as ccxt
import asyncio
from .base_exchange import BaseExchange
from loguru import logger


class OkxExchange(BaseExchange):
    """OKX exchange implementation"""
    
    def __init__(self):
        """Initialize the OKX exchange"""
        super().__init__("okx")
        self.exchange = ccxt.okx({
            'enableRateLimit': True,
            'timeout': 10000,  # 10 second timeout
        })
    
    async def fetch_orderbook(self, symbol):
        """
        Fetch orderbook for a symbol from OKX
        
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
            
            # OKX uses different symbol format for some pairs
            okx_symbol = symbol
            if symbol == "WIF/USDT":
                # Check if WIF/USDT exists, otherwise try alternative
                if "WIF/USDT" not in self.exchange.markets:
                    # OKX might use different naming
                    for market_symbol in self.exchange.markets:
                        if "WIF" in market_symbol and "USDT" in market_symbol:
                            okx_symbol = market_symbol
                            break
            
            # For other symbols, replace / with -
            if "/" in okx_symbol and okx_symbol not in self.exchange.markets:
                okx_symbol = symbol.replace("/", "-")
            
            if okx_symbol not in self.exchange.markets:
                # Try to find a similar symbol
                found = False
                for market_symbol in self.exchange.markets:
                    if symbol.replace("/", "").replace("-", "") in market_symbol.replace("/", "").replace("-", ""):
                        okx_symbol = market_symbol
                        found = True
                        break
                if not found:
                    raise ValueError(f"Symbol {symbol} not available on OKX")
            
            # Fetch orderbook with limit to reduce data size
            orderbook = await self.exchange.fetch_order_book(okx_symbol, limit=50)
            return orderbook
        except ccxt.NetworkError as e:
            logger.error(f"OKX network error for {symbol}: {str(e)}")
            raise Exception(f"OKX network error: {str(e)}")
        except ccxt.ExchangeError as e:
            logger.error(f"OKX exchange error for {symbol}: {str(e)}")
            raise Exception(f"OKX exchange error: {str(e)}")
        except ValueError as e:
            logger.error(f"OKX value error for {symbol}: {str(e)}")
            raise Exception(f"OKX value error: {str(e)}")
        except Exception as e:
            logger.error(f"OKX unexpected error for {symbol}: {str(e)}")
            raise Exception(f"OKX unexpected error: {str(e)}")
    
    async def close(self):
        """Close exchange connection"""
        try:
            await self.exchange.close()
        except Exception as e:
            logger.error(f"Error closing OKX connection: {str(e)}")