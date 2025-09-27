"""
Example usage script for the Crypto News Monitor
"""
import sys
import os

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from crypto_news_monitor.main import CryptoNewsMonitorApp


def example_usage():
    """
    Example of how to use the Crypto News Monitor
    """
    print("Crypto News Monitor - Example Usage")
    print("=" * 50)
    
    # Initialize the monitor with default configuration
    monitor = CryptoNewsMonitorApp()
    
    # Perform a single check to see current status
    print("\n1. Running single check...")
    monitor.run_single_check()
    
    print("\n2. To start continuous monitoring, call:")
    print("   monitor.start_continuous_monitoring()")
    print("\n   Or from command line:")
    print("   python -m crypto_news_monitor.main --mode continuous")
    
    print("\n3. For single check from command line:")
    print("   python -m crypto_news_monitor.main --mode single")
    
    print("\nExample completed!")


if __name__ == "__main__":
    example_usage()