"""
Data fetching module for cryptocurrency exchanges.
"""
import ccxt
import pandas as pd
from loguru import logger
from typing import List, Dict, Any


class DataFetcher:
    """Fetches cryptocurrency data from various exchanges."""
    
    def __init__(self, exchange_names: List[str]):
        """
        Initialize the DataFetcher with a list of exchange names.
        
        Args:
            exchange_names: List of exchange names to connect to
        """
        self.exchanges = {}
        self._initialize_exchanges(exchange_names)
    
    def _initialize_exchanges(self, exchange_names: List[str]):
        """Initialize connections to exchanges."""
        for name in exchange_names:
            try:
                exchange_class = getattr(ccxt, name)
                self.exchanges[name] = exchange_class({
                    'enableRateLimit': True,
                    'options': {
                        'adjustForTimeDifference': True
                    }
                })
                logger.info(f"Initialized exchange: {name}")
            except Exception as e:
                logger.error(f"Failed to initialize exchange {name}: {e}")
    
    def fetch_ohlcv(self, exchange_name: str, symbol: str, timeframe: str = '1h', 
                    limit: int = 100) -> pd.DataFrame:
        """
        Fetch OHLCV data for a symbol from an exchange.
        
        Args:
            exchange_name: Name of the exchange
            symbol: Trading pair symbol (e.g., 'BTC/USDT')
            timeframe: Timeframe for data (e.g., '1m', '1h', '1d')
            limit: Number of data points to fetch
            
        Returns:
            DataFrame with OHLCV data
        """
        if exchange_name not in self.exchanges:
            raise ValueError(f"Exchange {exchange_name} not initialized")
        
        try:
            exchange = self.exchanges[exchange_name]
            ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            
            # Convert to DataFrame
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            
            return df
        except Exception as e:
            logger.error(f"Failed to fetch data from {exchange_name} for {symbol}: {e}")
            return pd.DataFrame()
    
    def get_available_symbols(self, exchange_name: str) -> List[str]:
        """
        Get list of available trading symbols from an exchange.
        
        Args:
            exchange_name: Name of the exchange
            
        Returns:
            List of available symbols
        """
        if exchange_name not in self.exchanges:
            raise ValueError(f"Exchange {exchange_name} not initialized")
        
        try:
            exchange = self.exchanges[exchange_name]
            markets = exchange.load_markets()
            return list(markets.keys())
        except Exception as e:
            logger.error(f"Failed to fetch symbols from {exchange_name}: {e}")
            return []


def main():
    """Example usage of the DataFetcher."""
    fetcher = DataFetcher(['binance'])
    btc_data = fetcher.fetch_ohlcv('binance', 'BTC/USDT', '1h', 100)
    print(btc_data.head())


if __name__ == "__main__":
    main()