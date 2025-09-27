"""
3-Month High Price Tracker for cryptocurrency monitoring
Tracks crypto prices that have dropped 20% from their 3-month highs
"""
import pandas as pd
import numpy as np
import ccxt
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging
from pathlib import Path
import json
from loguru import logger

from crypto_price_monitor.data_fetcher import DataFetcher


class ThreeMonthHighTracker:
    """
    Tracks cryptocurrency prices that have dropped 20% from their 3-month highs
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the 3-month high tracker
        
        Args:
            config_path: Path to configuration file
        """
        # Load configuration
        self.config = self.load_config(config_path)
        
        # Extract configuration values from config
        self.exchanges = self.config.get('exchanges', ['binance'])
        self.trading_pairs = self.config.get('trading_pairs', ['BTC/USDT', 'ETH/USDT', 'SOL/USDT'])
        self.threshold = self.config.get('drop_threshold', 0.20)  # 20% drop
        self.refresh_rate = self.config.get('refresh_rate', 60)   # seconds
        self.data_dir = Path(self.config.get('data_dir', 'data/'))
        self.data_dir.mkdir(exist_ok=True)
        
        # Initialize data fetcher which also sets up exchanges
        self.data_fetcher = DataFetcher(self.exchanges)
        
        # Use the same exchange instances from the data fetcher
        self.exchange_instances = self.data_fetcher.exchanges
        
        # Cache for storing 3-month highs
        self.highs_cache = {}
        self.price_cache = {}
        
        logger.info("3-Month High Tracker initialized")
        logger.info(f"Tracking {len(self.trading_pairs)} pairs on {len(self.exchanges)} exchanges: {self.trading_pairs}")
    
    def load_config(self, config_path: Optional[str] = None) -> Dict:
        """
        Load configuration for the tracker
        
        Args:
            config_path: Path to configuration file
            
        Returns:
            Configuration dictionary
        """
        default_config = {
            'exchanges': ['binance'],
            'trading_pairs': ['BTC/USDT', 'ETH/USDT', 'SOL/USDT'],
            'drop_threshold': 0.20,
            'refresh_rate': 60,
            'data_dir': 'data/',
            'notification_method': 'console',
            'price_history_days': 90  # 3 months
        }
        
        if config_path and Path(config_path).exists():
            try:
                with open(config_path, 'r') as f:
                    import yaml
                    user_config = yaml.safe_load(f)
                    default_config.update(user_config)
            except Exception as e:
                logger.error(f"Could not load config from {config_path}: {e}. Using defaults.")
        
        return default_config
    
    
    
    def fetch_historical_data(self, exchange_name: str, symbol: str, 
                             days: int = 90, timeframe: str = '1d') -> pd.DataFrame:
        """
        Fetch historical OHLCV data for the past 'days' days
        
        Args:
            exchange_name: Name of the exchange
            symbol: Trading symbol (e.g., 'BTC/USDT')
            days: Number of days of history to fetch
            timeframe: Timeframe for data (e.g., '1d', '4h', '1h')
            
        Returns:
            DataFrame with OHLCV data
        """
        return self.data_fetcher.fetch_historical_data(exchange_name, symbol, days, timeframe)
    
    def calculate_three_month_high(self, price_data: pd.DataFrame) -> Tuple[float, datetime]:
        """
        Calculate the 3-month high from historical price data
        
        Args:
            price_data: DataFrame with historical price data
            
        Returns:
            Tuple of (high_price, high_datetime)
        """
        if price_data.empty or 'high' not in price_data.columns:
            return 0.0, datetime.now()
        
        # Find the highest high value and its timestamp
        max_high_idx = price_data['high'].idxmax()
        max_high_value = price_data.loc[max_high_idx, 'high']
        
        return max_high_value, max_high_idx
    
    def is_drop_alert(self, current_price: float, three_month_high: float) -> bool:
        """
        Check if current price is below the threshold from the 3-month high
        
        Args:
            current_price: Current market price
            three_month_high: 3-month high price
            
        Returns:
            True if current price is below the threshold
        """
        if three_month_high <= 0:
            return False
        
        # Calculate percentage drop
        drop_percentage = (three_month_high - current_price) / three_month_high
        
        return drop_percentage >= self.threshold
    
    def get_current_price(self, exchange_name: str, symbol: str) -> Optional[float]:
        """
        Get current price for a trading pair
        
        Args:
            exchange_name: Name of the exchange
            symbol: Trading symbol (e.g., 'BTC/USDT')
            
        Returns:
            Current price or None if error
        """
        return self.data_fetcher.get_current_price(exchange_name, symbol)
    
    def check_price_drop(self, exchange_name: str, symbol: str) -> Optional[Dict]:
        """
        Check if current price has dropped 20% from the 3-month high
        
        Args:
            exchange_name: Name of the exchange
            symbol: Trading symbol (e.g., 'BTC/USDT')
            
        Returns:
            Alert info if drop detected, None otherwise
        """
        exchange = self.exchange_instances.get(exchange_name)
        if not exchange:
            logger.error(f"Exchange {exchange_name} not initialized")
            return None

        # Get 3-month high
        high_info = self.highs_cache.get(f"{exchange_name}_{symbol}")
        if not high_info:
            # Fetch historical data to calculate 3-month high
            hist_data = self.fetch_historical_data(exchange_name, symbol)
            if hist_data.empty:
                logger.warning(f"Could not fetch historical data for {symbol}")
                return None
            
            three_month_high, high_datetime = self.calculate_three_month_high(hist_data)
            high_info = {
                'high': three_month_high,
                'timestamp': high_datetime.isoformat()
            }
            self.highs_cache[f"{exchange_name}_{symbol}"] = high_info
        else:
            three_month_high = high_info['high']

        # Get current price
        current_price = self.get_current_price(exchange_name, symbol)
        if current_price is None:
            logger.error(f"Could not fetch current price for {symbol}")
            return None

        # Check if price has dropped beyond threshold
        if self.is_drop_alert(current_price, three_month_high):
            drop_percentage = (three_month_high - current_price) / three_month_high * 100
            logger.info(f"ALERT: {symbol} on {exchange_name} has dropped {drop_percentage:.2f}% from 3-month high!")
            
            return {
                'exchange': exchange_name,
                'symbol': symbol,
                'current_price': current_price,
                'three_month_high': three_month_high,
                'drop_percentage': drop_percentage,
                'timestamp': datetime.now().isoformat(),
                'high_timestamp': high_info['timestamp']
            }

        # Update price cache for reference
        self.price_cache[f"{exchange_name}_{symbol}"] = {
            'price': current_price,
            'timestamp': datetime.now().isoformat()
        }

        return None
    
    def run_monitoring_cycle(self) -> List[Dict]:
        """
        Run one cycle of monitoring for all configured pairs
        
        Returns:
            List of alerts if any drops are detected
        """
        alerts = []
        
        for exchange_name in self.exchanges:
            exchange = self.exchange_instances.get(exchange_name)
            if not exchange:
                continue
            
            # Check each trading pair
            for symbol in self.trading_pairs:
                print('----checking ------' + symbol)
                try:
                    alert = self.check_price_drop(exchange_name, symbol)
                    if alert:
                        alerts.append(alert)
                except Exception as e:
                    logger.error(f"Error checking {symbol} on {exchange_name}: {e}")
        
        return alerts
    
    def start_monitoring(self):
        """
        Start the continuous monitoring process
        """
        logger.info("Starting 3-Month High Tracker monitoring...")
        
        try:
            while True:
                alerts = self.run_monitoring_cycle()
                
                # Process alerts
                for alert in alerts:
                    self.process_alert(alert)
                
                # Wait for refresh interval
                time.sleep(self.refresh_rate)
                
        except KeyboardInterrupt:
            logger.info("Monitoring stopped by user")
        except Exception as e:
            logger.error(f"Error in monitoring loop: {e}")
    
    def process_alert(self, alert: Dict):
        """
        Process an alert (send notification, log, etc.)
        
        Args:
            alert: Alert information dictionary
        """
        # Additional notification methods can be added here
        notification_method = self.config.get('notification_method', 'console')
        if notification_method == 'file':
            self._write_alert_to_file(alert)
    
    def _write_alert_to_file(self, alert: Dict):
        """
        Write alert to a log file
        
        Args:
            alert: Alert information dictionary
        """
        alerts_file = self.data_dir / "price_drop_alerts.json"
        
        # Read existing alerts
        existing_alerts = []
        if alerts_file.exists():
            try:
                with open(alerts_file, 'r') as f:
                    existing_alerts = json.load(f)
            except Exception:
                existing_alerts = []
        
        # Add new alert
        existing_alerts.append(alert)
        
        # Write back to file (keeping only last 100 alerts to prevent file bloat)
        with open(alerts_file, 'w') as f:
            json.dump(existing_alerts[-100:], f, indent=2)