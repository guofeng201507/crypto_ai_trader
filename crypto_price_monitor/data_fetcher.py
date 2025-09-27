"""
Data fetching module for the 3-month high tracker
"""
import ccxt
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from loguru import logger


class DataFetcher:
    """
    Handles data fetching from exchanges for the 3-month high tracker
    """
    
    def __init__(self, exchanges: List[str]):
        """
        Initialize the data fetcher
        
        Args:
            exchanges: List of exchange names to use
        """
        self.exchanges = {}
        self._setup_exchanges(exchanges)
    
    def _setup_exchanges(self, exchange_names: List[str]):
        """
        Setup exchange instances for data fetching
        
        Args:
            exchange_names: List of exchange names to initialize
        """
        for exchange_name in exchange_names:
            try:
                exchange_class = getattr(ccxt, exchange_name)
                self.exchanges[exchange_name] = exchange_class({
                    'enableRateLimit': True,
                    'timeout': 30000,
                })
                logger.info(f"Initialized {exchange_name} exchange")
            except Exception as e:
                logger.error(f"Could not initialize {exchange_name} exchange: {e}")
    
    def fetch_historical_data(self, exchange_name: str, symbol: str, 
                             days: int = 90, timeframe: str = '1d') -> Optional[pd.DataFrame]:
        """
        Fetch historical OHLCV data for the past 'days' days from specific exchange
        
        Args:
            exchange_name: Name of the exchange (e.g., 'binance')
            symbol: Trading symbol (e.g., 'BTC/USDT')
            days: Number of days of history to fetch
            timeframe: Timeframe for data (e.g., '1d', '4h', '1h')
            
        Returns:
            DataFrame with OHLCV data or None if error
        """
        exchange = self.exchanges.get(exchange_name)
        if not exchange:
            logger.error(f"Exchange {exchange_name} not found")
            return pd.DataFrame()
        
        try:
            # Calculate the timestamp for 'days' ago
            since = int((datetime.now() - timedelta(days=days)).timestamp() * 1000)
            
            # Fetch OHLCV data
            ohlcv = exchange.fetch_ohlcv(symbol, timeframe, since)
            
            if not ohlcv:
                logger.warning(f"No historical data for {symbol} on {exchange_name}")
                return pd.DataFrame()
            
            # Convert to DataFrame
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            
            return df
        except Exception as e:
            logger.error(f"Error fetching historical data for {symbol} on {exchange_name}: {e}")
            return pd.DataFrame()
    
    def fetch_multiple_exchanges(self, symbols: List[str], 
                                days: int = 90, 
                                timeframe: str = '1d') -> Dict[str, Dict[str, pd.DataFrame]]:
        """
        Fetch historical data for multiple symbols across all exchanges
        
        Args:
            symbols: List of symbols to fetch
            days: Number of days of history to fetch
            timeframe: Timeframe for data
            
        Returns:
            Dict of {exchange_name: {symbol: DataFrame}}
        """
        results = {}
        
        for exchange_name, exchange_instance in self.exchanges.items():
            results[exchange_name] = {}
            for symbol in symbols:
                df = self.fetch_historical_data(exchange_name, symbol, days, timeframe)
                if df is not None:
                    results[exchange_name][symbol] = df
                else:
                    results[exchange_name][symbol] = pd.DataFrame()
        
        return results
    
    def get_current_price(self, exchange_name: str, symbol: str) -> Optional[float]:
        """
        Get current price for a trading pair from specific exchange
        
        Args:
            exchange_name: Name of the exchange
            symbol: Trading symbol (e.g., 'BTC/USDT')
            
        Returns:
            Current price or None if error
        """
        exchange = self.exchanges.get(exchange_name)
        if not exchange:
            logger.error(f"Exchange {exchange_name} not found")
            return None
        
        try:
            ticker = exchange.fetch_ticker(symbol)
            return ticker['last'] if 'last' in ticker else ticker['close']
        except Exception as e:
            logger.error(f"Error fetching current price for {symbol} on {exchange_name}: {e}")
            return None