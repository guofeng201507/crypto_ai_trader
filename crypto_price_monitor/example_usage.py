"""
Example usage script for the 3-Month High Crypto Price Tracker
"""
import sys
import os

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from crypto_price_monitor.main import CryptoPriceMonitor


def example_usage():
    """
    Example of how to use the 3-Month High Crypto Price Tracker
    """
    print("3-Month High Crypto Price Tracker - Example Usage")
    print("=" * 50)
    
    # Initialize the monitor with default configuration
    monitor = CryptoPriceMonitor()
    
    # Perform a single check to see current status
    print("\n1. Running single check...")
    monitor.run_single_check()
    
    # Get current status of monitored assets
    print("\n2. Getting current status of monitored assets...")
    status_list = monitor.get_current_status()
    
    for status in status_list:
        print(f"   {status['symbol']}: Current ${status['current_price']:.4f}, "
              f"3-Month High ${status['three_month_high']:.4f}, "
              f"Drop {status['drop_percentage']:.2f}%")
    
    print("\n3. To start continuous monitoring, call:")
    print("   monitor.start_continuous_monitoring()")
    print("\n   Or from command line:")
    print("   python -m crypto_price_monitor.main --mode continuous")
    
    print("\n4. For single check from command line:")
    print("   python -m crypto_price_monitor.main --mode single")
    
    print("\n5. For status check from command line:")
    print("   python -m crypto_price_monitor.main --mode status")
    
    print("\nExample completed!")


if __name__ == "__main__":
    example_usage()