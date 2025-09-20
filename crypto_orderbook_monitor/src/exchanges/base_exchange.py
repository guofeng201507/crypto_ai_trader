"""
Base exchange class
"""
import ccxt
import asyncio
from abc import ABC, abstractmethod
from loguru import logger


class BaseExchange(ABC):
    """Base class for all exchanges"""
    
    def __init__(self, name):
        """
        Initialize the exchange
        
        Args:
            name (str): Exchange name
        """
        self.name = name
        self.exchange = None
    
    @abstractmethod
    async def fetch_orderbook(self, symbol):
        """
        Fetch orderbook for a symbol
        
        Args:
            symbol (str): Trading pair symbol
            
        Returns:
            dict: Orderbook data
            
        Raises:
            Exception: If there's an error fetching the orderbook
        """
        pass
    
    async def close(self):
        """Close exchange connection"""
        pass