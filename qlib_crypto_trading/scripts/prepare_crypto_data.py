"""
Data processing module for Qlib Crypto Trading
Handles data fetching, cleaning, and preparation for Qlib
"""
import os
import pandas as pd
import numpy as np
import qlib
from qlib.data import D
from qlib.config import REG_CN
from qlib.utils import init_instance_by_config
from qlib.data.dataset import DatasetH
from qlib.data.dataset.handler import DataHandlerLP
from qlib.contrib.data.handler import Alpha158
import ccxt
from datetime import datetime, timedelta
import logging
from loguru import logger


class CryptoDataProcessor:
    """
    A class to handle cryptocurrency data processing for Qlib
    """
    
    def __init__(self, config_path: str = None):
        """
        Initialize the CryptoDataProcessor
        
        Args:
            config_path: Path to the configuration file
        """
        self.config = self._load_config(config_path)
        self.exchanges = self._init_exchanges()
        
    def _load_config(self, config_path: str):
        """
        Load configuration from file
        """
        # In a real implementation, this would load from a YAML file
        # For now, we'll define a basic config
        config = {
            'crypto_pairs': ['BTC/USDT', 'ETH/USDT'],
            'exchanges': ['binance', 'coinbase'],
            'timeframe': '1h',
            'lookback_period': 365,  # days
        }
        return config
    
    def _init_exchanges(self):
        """
        Initialize CCXT exchange objects
        """
        exchanges = {}
        for exchange_name in self.config['exchanges']:
            exchange_class = getattr(ccxt, exchange_name)
            exchanges[exchange_name] = exchange_class({
                'enableRateLimit': True,
                'options': {
                    'adjustForTimeDifference': True
                }
            })
        return exchanges
    
    def fetch_historical_data(self, exchange_name: str, symbol: str, 
                              start_date: str, end_date: str, timeframe: str = '1h') -> pd.DataFrame:
        """
        Fetch historical data from an exchange
        
        Args:
            exchange_name: Name of the exchange (e.g., 'binance')
            symbol: Trading pair symbol (e.g., 'BTC/USDT')
            start_date: Start date in format 'YYYY-MM-DD'
            end_date: End date in format 'YYYY-MM-DD'
            timeframe: Time interval (e.g., '1m', '1h', '1d')
            
        Returns:
            DataFrame with OHLCV data
        """
        exchange = self.exchanges[exchange_name]
        
        # Convert dates to milliseconds
        start_timestamp = int(datetime.strptime(start_date, '%Y-%m-%d').timestamp() * 1000)
        end_timestamp = int(datetime.strptime(end_date, '%Y-%m-%d').timestamp() * 1000)
        
        # Fetch OHLCV data
        ohlcv = exchange.fetch_ohlcv(
            symbol=symbol,
            timeframe=timeframe,
            since=start_timestamp,
            limit=10000  # Adjust as needed
        )
        
        # Convert to DataFrame
        df = pd.DataFrame(ohlcv, columns=['datetime', 'open', 'high', 'low', 'close', 'volume'])
        df['datetime'] = pd.to_datetime(df['datetime'], unit='ms')
        df.set_index('datetime', inplace=True)
        
        # Filter by date range
        df = df[(df.index >= start_date) & (df.index <= end_date)]
        
        return df
    
    def prepare_qlib_data(self, data: pd.DataFrame, symbol: str) -> pd.DataFrame:
        """
        Prepare data in Qlib format
        
        Args:
            data: DataFrame with OHLCV data
            symbol: Trading symbol (e.g., 'BTC/USDT')
            
        Returns:
            DataFrame in Qlib format with instrument column
        """
        # Rename columns to match Qlib expectations
        data_renamed = data.rename(columns={
            'open': '$open',
            'high': '$high',
            'low': '$low',
            'close': '$close',
            'volume': '$volume'
        })
        
        # Add instrument column
        data_renamed['instrument'] = symbol
        
        # Add date column if needed
        data_renamed['date'] = data_renamed.index
        
        return data_renamed
    
    def save_to_qlib_format(self, data_dict: dict, qlib_data_path: str):
        """
        Save data to Qlib format
        
        Args:
            data_dict: Dictionary with symbol as key and DataFrame as value
            qlib_data_path: Path to save Qlib formatted data
        """
        # Qlib expects data in a specific directory structure
        # This is a simplified version - in practice, you'd use Qlib's data tooling
        
        # Create the directory if it doesn't exist
        os.makedirs(qlib_data_path, exist_ok=True)
        
        # In a real implementation, you would use Qlib's dump_bin tool
        # For this example, we'll just save as CSV files
        for symbol, df in data_dict.items():
            # Replace '/' with '_' for filename
            filename = f"{symbol.replace('/', '_')}.csv"
            filepath = os.path.join(qlib_data_path, filename)
            df.to_csv(filepath)
    
    def run_data_pipeline(self, output_path: str):
        """
        Run the complete data processing pipeline
        
        Args:
            output_path: Path to save processed data
        """
        logger.info("Starting data processing pipeline...")
        
        all_data = {}
        
        for exchange_name in self.config['exchanges']:
            for symbol in self.config['crypto_pairs']:
                logger.info(f"Fetching data for {symbol} on {exchange_name}")
                
                # Calculate date range
                end_date = datetime.now().strftime('%Y-%m-%d')
                start_date = (datetime.now() - timedelta(days=self.config['lookback_period'])).strftime('%Y-%m-%d')
                
                try:
                    # Fetch historical data
                    raw_data = self.fetch_historical_data(
                        exchange_name=exchange_name,
                        symbol=symbol,
                        start_date=start_date,
                        end_date=end_date,
                        timeframe=self.config['timeframe']
                    )
                    
                    # Prepare for Qlib
                    qlib_data = self.prepare_qlib_data(raw_data, symbol)
                    
                    # Store data
                    all_data[symbol] = qlib_data
                    
                    logger.info(f"Successfully processed data for {symbol}")
                    
                except Exception as e:
                    logger.error(f"Error processing {symbol} on {exchange_name}: {str(e)}")
        
        # Save all data
        self.save_to_qlib_format(all_data, output_path)
        logger.info("Data processing pipeline completed!")
        
        return all_data


def init_qlib(qlib_dir: str = "~/.qlib/qlib_data/cryptocurrency", region: str = "crypto", freq: str = "1min"):
    """
    Initialize Qlib with cryptocurrency settings
    
    Args:
        qlib_dir: Directory where Qlib data is stored
        region: Region setting (using 'crypto' for cryptocurrency)
        freq: Frequency of the data
    """
    qlib.init(
        provider_uri=qlib_dir,
        region=region,
        freq=freq
    )


if __name__ == "__main__":
    # Example usage
    processor = CryptoDataProcessor()
    
    # Initialize Qlib
    init_qlib()
    
    # Run data pipeline
    output_dir = "./data/qlib_crypto_data"
    crypto_data = processor.run_data_pipeline(output_dir)
    
    print("Data processing complete!")
    print(f"Processed data for symbols: {list(crypto_data.keys())}")