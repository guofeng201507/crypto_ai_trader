"""
Test script to verify MCP server functionality
"""
import sys
import os

# Add the trade_chatbot backend to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'trade_chatbot/backend'))

from trade_chatbot.backend.utils.helpers import get_mcp_data, get_stock_data

def test_mcp_functionality():
    print("Testing MCP server functionality...")
    
    # Test with a common stock symbol
    symbols_to_test = ['AAPL', 'GOOGL', 'MSFT', 'TSLA']
    
    for symbol in symbols_to_test:
        print(f"\nTesting symbol: {symbol}")
        
        # Test the MCP-specific function
        mcp_result = get_mcp_data(symbol)
        if mcp_result:
            print(f"  ✓ MCP server returned data for {symbol}:")
            print(f"    Price: ${mcp_result.get('price', 'N/A')}")
            print(f"    Change: {mcp_result.get('change', 'N/A')} ({mcp_result.get('change_percent', 'N/A')})")
        else:
            print(f"  ✗ MCP server failed for {symbol}")
            
        # Test the general function that uses Yahoo as primary and MCP as fallback
        general_result = get_stock_data(symbol)
        if general_result:
            print(f"  ✓ General function returned data for {symbol}:")
            print(f"    Price: ${general_result.get('price', 'N/A')}")
            print(f"    Source: {general_result.get('source', 'N/A')}")
        else:
            print(f"  ✗ General function failed for {symbol}")

if __name__ == "__main__":
    test_mcp_functionality()