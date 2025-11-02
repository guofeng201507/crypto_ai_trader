"""
Test script to specifically test different method names for the Alpha Vantage MCP server
"""
import requests
import os
from dotenv import load_dotenv
import json
import logging

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_with_different_methods():
    """Test with different method names that might be supported"""
    print("\n=== Testing with Alternative Method Names ===")
    
    api_key = os.environ.get('ALPHA_VANTAGE_API_KEY', '20KCRQCE82CTCDVI')
    mcp_url = 'https://mcp.alphavantage.co/mcp'
    
    # Try different method names that might work based on typical patterns
    methods_and_symbols = [
        ("alpha_vantage.global_quote", "AAPL"),
        ("global_quote", "AAPL"),
        ("quote", "AAPL"),
        ("get_quote", "AAPL"),
        ("time_series_daily", "AAPL"),
        ("alpha_vantage.time_series_daily", "AAPL"),
        ("alpha_vantage.forex.rate", "EURUSD"),  # For forex
        ("alpha_vantage.crypto.daily", "BTC"),   # For crypto
        ("alpha_vantage.tech_indicators", "AAPL"),  # For technical indicators
    ]
    
    for method, symbol in methods_and_symbols:
        print(f"\nTesting method: {method} with symbol: {symbol}")
        
        payload = {
            "jsonrpc": "2.0",
            "method": method,
            "params": {
                "symbol": symbol
            },
            "id": 1
        }
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        try:
            response = requests.post(
                mcp_url,
                data=json.dumps(payload),
                headers=headers
            )
            
            logger.info(f"Method {method} response status: {response.status_code}")
            logger.info(f"Method {method} response: {response.text}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if "result" in data:
                        print(f"  ✓ Success with method {method}")
                        print(f"    Result keys: {list(data['result'].keys()) if 'result' in data and data['result'] else 'None'}")
                        print(f"    First few result details: {str(data['result'])[:200]}...")
                    elif "error" in data:
                        print(f"  ✗ API Error with method {method}: {data['error']['message'] if isinstance(data['error'], dict) else data['error']}")
                    else:
                        print(f"  ? Different response format with method {method}: {data}")
                except json.JSONDecodeError:
                    print(f"  ✗ Response not valid JSON with method {method}")
            else:
                print(f"  ✗ HTTP Error with method {method}: {response.status_code}")
                
        except Exception as e:
            print(f"  ✗ Exception with method {method}: {str(e)}")

if __name__ == "__main__":
    test_with_different_methods()