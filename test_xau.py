#!/usr/bin/env python3
"""
Test script to verify XAU/USD price fetching
"""
import sys
import os

# Add the trade_chatbot backend to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'trade_chatbot/backend'))

from trade_chatbot.backend.utils.helpers import get_stock_data

def test_xau_usd():
    print("Testing XAU/USD price fetching...")
    
    # Test both formats: XAU/USD and XAUUSD
    symbols_to_test = ['XAU/USD', 'XAUUSD', 'XAU']
    
    for symbol in symbols_to_test:
        print(f"\nTesting symbol: {symbol}")
        result = get_stock_data(symbol)
        print(f"Result: {result}")
        if result:
            print(f"Successfully fetched data for {symbol}")
            print(f"Symbol: {result.get('symbol')}")
            print(f"Price: {result.get('price')}")
        else:
            print(f"Failed to fetch data for {symbol}")

if __name__ == "__main__":
    test_xau_usd()