"""
Test script specifically for MCP server approach
This focuses on testing the Alpha Vantage MCP server with proper JSON-RPC format
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

def test_jsonrpc_mcp():
    """Test direct JSON-RPC call to MCP server with proper authentication"""
    print("\n=== Testing MCP Server with JSON-RPC ===")
    
    api_key = os.environ.get('ALPHA_VANTAGE_API_KEY', '20KCRQCE82CTCDVI')
    mcp_url = 'https://mcp.alphavantage.co/mcp'
    
    # Test with a valid symbol
    symbols = ['AAPL'] #, 'GOOGL', 'MSFT', 'TSLA'
    
    for symbol in symbols:
        print(f"\nTesting symbol: {symbol}")
        
        # Prepare the JSON-RPC request
        # Move the apikey to Authorization header instead of params
        payload = {
            "jsonrpc": "2.0",
            "method": "alpha_vantage.global_quote",
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
            logger.info(f"Making JSON-RPC request to: {mcp_url}")
            logger.info(f"Headers: {headers}")
            logger.info(f"Payload: {json.dumps(payload, indent=2)}")
            
            response = requests.post(
                mcp_url,
                data=json.dumps(payload),
                headers=headers
            )
            
            logger.info(f"Response status: {response.status_code}")
            logger.info(f"Response text: {response.text}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    logger.info(f"Response JSON: {json.dumps(data, indent=2)}")
                    
                    if "result" in data:
                        print(f"  ✓ Successfully got data for {symbol}")
                        quote = data["result"]
                        print(f"    Symbol: {quote.get('01. symbol', 'N/A')}")
                        print(f"    Price: {quote.get('05. price', 'N/A')}")
                        print(f"    Change: {quote.get('09. change', 'N/A')}")
                    elif "error" in data:
                        print(f"  ✗ API Error for {symbol}: {data['error']}")
                    else:
                        print(f"  ? Unexpected response format for {symbol}: {data}")
                except json.JSONDecodeError:
                    print(f"  ✗ Response is not valid JSON for {symbol}: {response.text}")
            else:
                print(f"  ✗ HTTP Error for {symbol}: {response.status_code}")
                print(f"    Response: {response.text}")
                
        except Exception as e:
            print(f"  ✗ Exception for {symbol}: {str(e)}")

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
        ("alpha_vantage.time_series_daily", "AAPL")
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
                    elif "error" in data:
                        print(f"  ✗ API Error with method {method}: {data['error']}")
                    else:
                        print(f"  ? Different response format with method {method}: {data}")
                except json.JSONDecodeError:
                    print(f"  ✗ Response not valid JSON with method {method}")
            else:
                print(f"  ✗ HTTP Error with method {method}: {response.status_code}")
                
        except Exception as e:
            print(f"  ✗ Exception with method {method}: {str(e)}")

def test_list_functions():
    """Test to list all available functions from the MCP server"""
    print("\n=== Listing Available Functions from MCP Server ===")
    
    api_key = os.environ.get('ALPHA_VANTAGE_API_KEY', '20KCRQCE82CTCDVI')
    mcp_url = 'https://mcp.alphavantage.co/mcp'
    
    # Try to call a method that might list available functions
    # This might not exist, but it's worth trying standard JSON-RPC methods
    payloads_to_try = [
        {
            "jsonrpc": "2.0",
            "method": "system.describe",
            "params": {},
            "id": 1
        },
        {
            "jsonrpc": "2.0",
            "method": "rpc.discover",
            "params": {},
            "id": 1
        },
        {
            "jsonrpc": "2.0",
            "method": "system.listMethods",
            "params": {},
            "id": 1
        },
        {
            "jsonrpc": "2.0",
            "method": "get_available_functions",
            "params": {},
            "id": 1
        }
    ]
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    for i, payload in enumerate(payloads_to_try):
        method = payload["method"]
        print(f"\nTrying to list functions with method: {method}")
        
        try:
            response = requests.post(mcp_url, json=payload, headers=headers)
            
            logger.info(f"List functions method {method} response status: {response.status_code}")
            logger.info(f"List functions method {method} response: {response.text}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if "result" in data:
                        print(f"  ✓ Found functions with {method}:")
                        print(f"    Result: {data['result']}")
                    elif "error" in data:
                        print(f"  ✗ Error with {method}: {data['error']['message']}")
                    else:
                        print(f"  ? Different response with {method}: {data}")
                except json.JSONDecodeError:
                    print(f"  ✗ Response not valid JSON with {method}")
            else:
                print(f"  ✗ HTTP Error with {method}: {response.status_code}")
                
        except Exception as e:
            print(f"  ✗ Exception with {method}: {str(e)}")

def test_with_regular_api():
    """Test with regular API endpoint as fallback"""
    print("\n=== Testing Regular Alpha Vantage API ===")
    
    api_key = os.environ.get('ALPHA_VANTAGE_API_KEY', '20KCRQCE82CTCDVI')
    base_url = 'https://www.alphavantage.co/query'
    
    symbol = 'AAPL'
    params = {
        'function': 'GLOBAL_QUOTE',
        'symbol': symbol,
        'apikey': api_key
    }
    
    try:
        response = requests.get(base_url, params=params)
        logger.info(f"Regular API response status: {response.status_code}")
        logger.info(f"Regular API response: {response.text}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                if "Global Quote" in data:
                    print(f"  ✓ Regular API works: {symbol}")
                    quote = data["Global Quote"]
                    print(f"    Price: {quote.get('05. price', 'N/A')}")
                else:
                    print(f"  ? Regular API returned different format: {data}")
            except json.JSONDecodeError:
                print(f"  ✗ Regular API response not valid JSON")
        else:
            print(f"  ✗ Regular API HTTP Error: {response.status_code}")
            
    except Exception as e:
        print(f"  ✗ Regular API Exception: {str(e)}")

if __name__ == "__main__":
    print("MCP Server Test Tool")
    print("Testing different approaches to call Alpha Vantage API")
    
    # Run all tests
    test_jsonrpc_mcp()
    test_with_different_methods()
    test_list_functions()
    test_with_regular_api()
    
    print("\n=== MCP Test Complete ===")
    print("Check the logs above to determine which approach works")