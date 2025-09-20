#!/usr/bin/env python3
"""
Simple test script for the orderbook monitor
"""

import asyncio
import sys
import os

# Add src to path for imports
src_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src')
sys.path.insert(0, src_path)

from exchanges.binance import BinanceExchange
from exchanges.okx import OkxExchange
from exchanges.coinbase import CoinbaseExchange


async def test_exchanges():
    """Test exchange connections"""
    print("Testing exchange connections...")
    
    # Test Binance
    print("Testing Binance...")
    try:
        binance = BinanceExchange()
        orderbook = await binance.fetch_orderbook("SOL/USDT")
        print(f"Binance SOL/USDT orderbook fetched successfully. Bids: {len(orderbook['bids'])}, Asks: {len(orderbook['asks'])}")
        await binance.close()
    except Exception as e:
        print(f"Error testing Binance: {e}")
    
    # Test OKX
    print("Testing OKX...")
    try:
        okx = OkxExchange()
        orderbook = await okx.fetch_orderbook("SOL/USDT")
        print(f"OKX SOL/USDT orderbook fetched successfully. Bids: {len(orderbook['bids'])}, Asks: {len(orderbook['asks'])}")
        await okx.close()
    except Exception as e:
        print(f"Error testing OKX: {e}")
    
    # Test Coinbase
    print("Testing Coinbase...")
    try:
        coinbase = CoinbaseExchange()
        orderbook = await coinbase.fetch_orderbook("SOL/USDT")
        print(f"Coinbase SOL/USDT orderbook fetched successfully. Bids: {len(orderbook['bids'])}, Asks: {len(orderbook['asks'])}")
        await coinbase.close()
    except Exception as e:
        print(f"Error testing Coinbase: {e}")


if __name__ == "__main__":
    asyncio.run(test_exchanges())