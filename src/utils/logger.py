"""
Logging and monitoring utilities.
"""
import os
import sys
from loguru import logger
from datetime import datetime
from typing import Dict, Any


class LogManager:
    """Manages application logging."""
    
    def __init__(self, logs_dir: str = "logs/", log_level: str = "INFO"):
        """
        Initialize the LogManager.
        
        Args:
            logs_dir: Directory to store log files
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        self.logs_dir = logs_dir
        self.log_level = log_level
        
        # Create logs directory if it doesn't exist
        os.makedirs(logs_dir, exist_ok=True)
        
        # Remove default logger
        logger.remove()
        
        # Add file logger
        log_file = os.path.join(logs_dir, f"trader_{datetime.now().strftime('%Y%m%d')}.log")
        logger.add(log_file, level=log_level, rotation="500 MB", retention="10 days")
        
        # Add console logger
        logger.add(sys.stderr, level=log_level)
        
        logger.info("LogManager initialized")
    
    def get_logger(self):
        """Get the configured logger."""
        return logger


class PerformanceMonitor:
    """Monitors application performance."""
    
    def __init__(self):
        """Initialize the PerformanceMonitor."""
        self.metrics = {}
    
    def record_metric(self, name: str, value: Any):
        """
        Record a performance metric.
        
        Args:
            name: Metric name
            value: Metric value
        """
        self.metrics[name] = value
        logger.debug(f"Recorded metric: {name} = {value}")
    
    def record_trade_performance(self, symbol: str, entry_price: float, 
                               exit_price: float, position_size: float):
        """
        Record trade performance metrics.
        
        Args:
            symbol: Trading symbol
            entry_price: Entry price
            exit_price: Exit price
            position_size: Position size
        """
        profit = (exit_price - entry_price) * position_size
        profit_percent = (exit_price - entry_price) / entry_price * 100
        
        self.record_metric(f"{symbol}_trade_profit", profit)
        self.record_metric(f"{symbol}_trade_profit_percent", profit_percent)
        
        logger.info(f"Trade completed for {symbol}: {profit_percent:.2f}% profit")
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get all recorded metrics."""
        return self.metrics.copy()


def main():
    """Example usage of the logging and monitoring utilities."""
    # Initialize log manager
    log_manager = LogManager()
    logger = log_manager.get_logger()
    
    # Test logging
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    
    # Test performance monitor
    monitor = PerformanceMonitor()
    monitor.record_metric("test_metric", 42)
    monitor.record_trade_performance("BTC/USDT", 30000, 31000, 1.0)
    
    print("Recorded metrics:", monitor.get_metrics())


if __name__ == "__main__":
    main()