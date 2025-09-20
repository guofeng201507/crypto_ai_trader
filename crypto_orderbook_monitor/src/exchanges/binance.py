"""
Binance exchange implementation
"""
import ccxt.async_support as ccxt
import asyncio
from .base_exchange import BaseExchange


class BinanceExchange(BaseExchange):
    """Binance exchange implementation"""
    
    def __init__(self):
        """Initialize the Binance exchange"""
        super().__init__("binance")
        self.exchange = ccxt.binance({
            'enableRateLimit': True,
        })
    
    async def fetch_orderbook(self, symbol):
        """
        Fetch orderbook for a symbol from Binance
        
        Args:
            symbol (str): Trading pair symbol
            
        Returns:
            dict: Orderbook data
        """
        try:
            # Validate symbol exists
            if not self.exchange.markets:
                await self.exchange.load_markets()
            
            if symbol not in self.exchange.markets:
                raise ValueError(f"Symbol {symbol} not available on Binance")
            
            # Fetch orderbook
            orderbook = await self.exchange.fetch_order_book(symbol)
            return orderbook
        except Exception as e:
            raise Exception(f"Binance fetch_orderbook error: {str(e)}")
    
    async def close(self):
        """Close exchange connection"""
        try:
            await self.exchange.close()
        except:
            pass