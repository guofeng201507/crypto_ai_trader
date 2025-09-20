"""
OKX exchange implementation
"""
import ccxt.async_support as ccxt
import asyncio
from .base_exchange import BaseExchange


class OkxExchange(BaseExchange):
    """OKX exchange implementation"""
    
    def __init__(self):
        """Initialize the OKX exchange"""
        super().__init__("okx")
        self.exchange = ccxt.okx({
            'enableRateLimit': True,
        })
    
    async def fetch_orderbook(self, symbol):
        """
        Fetch orderbook for a symbol from OKX
        
        Args:
            symbol (str): Trading pair symbol
            
        Returns:
            dict: Orderbook data
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
            
            # Fetch orderbook
            orderbook = await self.exchange.fetch_order_book(okx_symbol)
            return orderbook
        except Exception as e:
            raise Exception(f"OKX fetch_orderbook error: {str(e)}")
    
    async def close(self):
        """Close exchange connection"""
        try:
            await self.exchange.close()
        except:
            pass