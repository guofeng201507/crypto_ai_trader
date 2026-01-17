"""Main entry point for the crypto futures monitor."""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from crypto_futures_monitor.futures_monitor import main

if __name__ == "__main__":
    main()
