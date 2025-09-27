"""
Main module for the 3-month crypto price high tracker
"""
import time
from datetime import datetime
from typing import List, Dict
from loguru import logger

from crypto_price_monitor.high_tracker import ThreeMonthHighTracker
from crypto_price_monitor.notification_manager import NotificationManager
from crypto_price_monitor.config_manager import ConfigManager


class CryptoPriceMonitor:
    """
    Main class that orchestrates the 3-month high tracking system
    """
    
    def __init__(self, config_path: str = None):
        """
        Initialize the crypto price monitor
        
        Args:
            config_path: Path to configuration file
        """
        # Initialize configuration
        self.config_manager = ConfigManager(config_path)
        self.config = self.config_manager.config
        
        # Initialize the high tracker
        self.high_tracker = ThreeMonthHighTracker(config_path)
        
        # Initialize notification manager
        self.notification_manager = NotificationManager(self.config)
        
        logger.info("Crypto Price Monitor initialized")
    
    def run_monitoring_cycle(self) -> List[Dict]:
        """
        Run one complete monitoring cycle
        
        Returns:
            List of alerts if any drops detected
        """
        logger.info("Starting monitoring cycle...")
        
        # Run the tracking cycle
        alerts = self.high_tracker.run_monitoring_cycle()
        
        # Process each alert
        for alert in alerts:
            self.notification_manager.process_alert(alert)
        
        logger.info(f"Monitoring cycle completed. Found {len(alerts)} alerts.")
        
        return alerts
    
    def start_continuous_monitoring(self):
        """
        Start the continuous monitoring process
        """
        logger.info("Starting continuous monitoring...")
        
        try:
            while True:
                alerts = self.run_monitoring_cycle()
                
                # Wait for refresh interval
                refresh_rate = self.config.get('refresh_rate', 60)
                time.sleep(refresh_rate)
                
        except KeyboardInterrupt:
            logger.info("Monitoring stopped by user")
        except Exception as e:
            logger.error(f"Error in monitoring loop: {e}")
    
    def run_single_check(self):
        """
        Run a single check and return results without continuous monitoring
        """
        logger.info("Running single check...")
        
        alerts = self.run_monitoring_cycle()
        
        if alerts:
            print(f"\nFound {len(alerts)} significant drops from 3-month highs:")
            for alert in alerts:
                print(f"- {alert['symbol']} on {alert['exchange']}: dropped {alert['drop_percentage']:.2f}%")
        else:
            print("\nNo significant drops from 3-month highs detected.")
    
    def get_current_status(self):
        """
        Get current status of monitored assets
        """
        logger.info("Getting current status...")
        
        status_list = []
        
        for exchange_name in self.config['exchanges']:
            exchange = self.high_tracker.exchange_instances.get(exchange_name)
            if not exchange:
                continue
            
            for symbol in self.config['trading_pairs']:
                try:
                    # Get current price
                    current_price = self.high_tracker.get_current_price(exchange, symbol)
                    
                    # Get 3-month high
                    high_info = self.high_tracker.highs_cache.get(f"{exchange_name}_{symbol}")
                    if not high_info:
                        # Fetch historical data to calculate 3-month high
                        hist_data = self.high_tracker.fetch_historical_data(exchange, symbol)
                        if not hist_data.empty:
                            three_month_high, high_datetime = self.high_tracker.calculate_three_month_high(hist_data)
                            high_info = {
                                'high': three_month_high,
                                'timestamp': high_datetime.isoformat()
                            }
                            self.high_tracker.highs_cache[f"{exchange_name}_{symbol}"] = high_info
                        else:
                            logger.warning(f"Could not fetch historical data for {symbol}")
                            continue
                    
                    if current_price and high_info['high'] > 0:
                        drop_percentage = (high_info['high'] - current_price) / high_info['high'] * 100
                        
                        status = {
                            'exchange': exchange_name,
                            'symbol': symbol,
                            'current_price': current_price,
                            'three_month_high': high_info['high'],
                            'drop_percentage': drop_percentage,
                            'timestamp': datetime.now().isoformat()
                        }
                        
                        status_list.append(status)
                        
                except Exception as e:
                    logger.error(f"Error getting status for {symbol} on {exchange_name}: {e}")
        
        return status_list


def main():
    """
    Main function to run the crypto price monitor
    """
    import argparse
    
    parser = argparse.ArgumentParser(description='Crypto Price Monitor - Track 3-Month Highs')
    parser.add_argument('--config', type=str, default=None,
                        help='Path to configuration file')
    parser.add_argument('--mode', choices=['continuous', 'single', 'status'], default='continuous',
                        help='Operation mode: continuous monitoring, single check, or status')
    
    args = parser.parse_args()
    
    # Initialize the monitor
    monitor = CryptoPriceMonitor(args.config)
    
    if args.mode == 'single':
        monitor.run_single_check()
    elif args.mode == 'status':
        status_list = monitor.get_current_status()
        print(f"\nCurrent status for {len(status_list)} assets:")
        for status in status_list:
            print(f"- {status['symbol']}: Current ${status['current_price']:.4f}, "
                  f"3-Month High ${status['three_month_high']:.4f}, "
                  f"Drop {status['drop_percentage']:.2f}%")
    else:  # continuous mode
        monitor.start_continuous_monitoring()


if __name__ == "__main__":
    main()