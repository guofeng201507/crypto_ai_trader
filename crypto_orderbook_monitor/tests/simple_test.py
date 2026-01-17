#!/usr/bin/env python3
"""
Simple test for the orderbook monitor
"""

import asyncio
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from exchanges.binance import BinanceExchange
from exchanges.okx import OkxExchange
from exchanges.coinbase import CoinbaseExchange


async def test():
    """Test the exchanges"""
    print("Testing exchanges...")
    
    # Test Binance
    print("Testing Binance SOL/USDT...")
    try:
        binance = BinanceExchange()
        orderbook = await binance.fetch_orderbook("SOL/USDT")
        print(f"  Best bid: {orderbook['bids'][0][0]} (vol: {orderbook['bids'][0][1]})")
        print(f"  Best ask: {orderbook['asks'][0][0]} (vol: {orderbook['asks'][0][1]})")
        await binance.close()
    except Exception as e:
        print(f"  Error: {e}")
    
    # Test OKX
    print("Testing OKX SOL/USDT...")
    try:
        okx = OkxExchange()
        orderbook = await okx.fetch_orderbook("SOL/USDT")
        print(f"  Best bid: {orderbook['bids'][0][0]} (vol: {orderbook['bids'][0][1]})")
        print(f"  Best ask: {orderbook['asks'][0][0]} (vol: {orderbook['asks'][0][1]})")
        await okx.close()
    except Exception as e:
        print(f"  Error: {e}")
    
    # Test Coinbase
    print("Testing Coinbase SOL/USDT...")
    try:
        coinbase = CoinbaseExchange()
        orderbook = await coinbase.fetch_orderbook("SOL/USDT")
        print(f"  Best bid: {orderbook['bids'][0][0]} (vol: {orderbook['bids'][0][1]})")
        print(f"  Best ask: {orderbook['asks'][0][0]} (vol: {orderbook['asks'][0][1]})")
        await coinbase.close()
    except Exception as e:
        print(f"  Error: {e}")


if __name__ == "__main__":
    asyncio.run(test())