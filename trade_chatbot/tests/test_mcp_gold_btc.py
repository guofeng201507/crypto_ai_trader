"""
Test script to specifically test MCP server functionality for gold and BTC
"""
import sys
import os

# Add the trade_chatbot backend to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'trade_chatbot/backend'))

from trade_chatbot.backend.utils.helpers import get_mcp_data, get_stock_data

def test_mcp_gold_btc():
    print("Testing MCP server functionality for Gold and BTC...")
    
    # Test with symbols that might be used for Gold and BTC
    symbols_to_test = [
        'XAUUSD',  # Gold in USD
        'XAGUSD',  # Silver in USD 
        'BTCUSD',  # Bitcoin in USD (Yahoo Finance format)
        'BTC-USD', # Bitcoin in USD (Crypto format)
        'ETHUSD',  # Ethereum in USD (Yahoo Finance format)
        'ETH-USD', # Ethereum in USD (Crypto format)
    ]
    
    for symbol in symbols_to_test:
        print(f"\nTesting symbol: {symbol}")
        
        # Test the MCP-specific function
        print("  Testing MCP server directly...")
        mcp_result = get_mcp_data(symbol)
        if mcp_result:
            print(f"    ✓ MCP server returned data for {symbol}:")
            print(f"      Symbol: {mcp_result.get('symbol', 'N/A')}")
            print(f"      Price: ${mcp_result.get('price', 'N/A')}")
            print(f"      Change: {mcp_result.get('change', 'N/A')} ({mcp_result.get('change_percent', 'N/A')})")
            print(f"      Volume: {mcp_result.get('volume', 'N/A')}")
        else:
            print(f"    ✗ MCP server failed for {symbol}")
            
        # Test the general function that uses Yahoo as primary and MCP as fallback
        print("  Testing general data retrieval function...")
        general_result = get_stock_data(symbol)
        if general_result:
            print(f"    ✓ General function returned data for {symbol}:")
            print(f"      Symbol: {general_result.get('symbol', 'N/A')}")
            print(f"      Price: ${general_result.get('price', 'N/A')}")
            print(f"      Change: {general_result.get('change', 'N/A')} ({general_result.get('change_percent', 'N/A')})")
            print(f"      Volume: {general_result.get('volume', 'N/A')}")
        else:
            print(f"    ✗ General function failed for {symbol}")

    # Also test natural language input that might be used
    print(f"\nTesting natural language interpretations...")
    natural_inputs = [
        'XAU',  # Gold
        'BTC',  # Bitcoin
        'ETH',  # Ethereum
    ]
    
    for symbol in natural_inputs:
        print(f"\nTesting natural symbol: {symbol}")
        result = get_stock_data(symbol)
        if result:
            print(f"    ✓ Data returned for {symbol}:")
            print(f"      Symbol: {result.get('symbol', 'N/A')}")
            print(f"      Price: ${result.get('price', 'N/A')}")
            print(f"      Change: {result.get('change', 'N/A')} ({result.get('change_percent', 'N/A')})")
        else:
            print(f"    ✗ Data retrieval failed for {symbol}")

if __name__ == "__main__":
    test_mcp_gold_btc()