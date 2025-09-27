"""
Main module for the Crypto News Monitor
"""
import time
from typing import List, Dict
from loguru import logger

from crypto_news_monitor.news_monitor import CryptoNewsMonitor


class CryptoNewsMonitorApp:
    """
    Main class that orchestrates the crypto news monitoring system
    """
    
    def __init__(self, config_path: str = None):
        """
        Initialize the crypto news monitor app
        
        Args:
            config_path: Path to configuration file
        """
        # Initialize the news monitor
        self.news_monitor = CryptoNewsMonitor(config_path)
        
        logger.info("Crypto News Monitor App initialized")
    
    def run_monitoring_cycle(self) -> List[Dict]:
        """
        Run one complete monitoring cycle
        
        Returns:
            List of new articles if any are found
        """
        logger.info("Starting monitoring cycle...")
        
        # Run the tracking cycle
        new_articles = self.news_monitor.run_monitoring_cycle()
        
        # Process each new article
        for article in new_articles:
            self.news_monitor.process_new_article(article)
        
        logger.info(f"Monitoring cycle completed. Found {len(new_articles)} new articles.")
        
        return new_articles
    
    def start_continuous_monitoring(self):
        """
        Start the continuous monitoring process
        """
        logger.info("Starting continuous news monitoring...")
        
        try:
            while True:
                new_articles = self.run_monitoring_cycle()
                
                # Wait for refresh interval
                refresh_rate = self.news_monitor.config.get('refresh_rate', 300)
                time.sleep(refresh_rate)
                
        except KeyboardInterrupt:
            logger.info("Monitoring stopped by user")
        except Exception as e:
            logger.error(f"Error in monitoring loop: {e}")
    
    def run_single_check(self):
        """
        Run a single check and return results without continuous monitoring
        """
        logger.info("Running single news check...")
        
        new_articles = self.run_monitoring_cycle()
        
        if new_articles:
            print(f"\nFound {len(new_articles)} new relevant articles:")
            for article in new_articles:
                print(f"- {article['title']}")
                print(f"  Keywords: {', '.join(article['relevant_keywords'])}")
                print(f"  URL: {article['url']}")
                print()
        else:
            print("\nNo new relevant articles found.")


def main():
    """
    Main function to run the crypto news monitor
    """
    import argparse
    
    parser = argparse.ArgumentParser(description='Crypto News Monitor - Track Crypto News')
    parser.add_argument('--config', type=str, default=None,
                        help='Path to configuration file')
    parser.add_argument('--mode', choices=['continuous', 'single'], default='continuous',
                        help='Operation mode: continuous monitoring or single check')
    
    args = parser.parse_args()
    
    # Initialize the monitor
    monitor = CryptoNewsMonitorApp(args.config)
    
    if args.mode == 'single':
        monitor.run_single_check()
    else:  # continuous mode
        monitor.start_continuous_monitoring()


if __name__ == "__main__":
    main()