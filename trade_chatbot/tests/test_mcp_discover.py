"""
Test script to check available methods on the Alpha Vantage MCP server
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
        },
        {
            "jsonrpc": "2.0",
            "method": "server.info",
            "params": {},
            "id": 1
        },
        {
            "jsonrpc": "2.0",
            "method": "help",
            "params": {},
            "id": 1
        },
        {
            "jsonrpc": "2.0",
            "method": "version",
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
                        print(f"  ✗ Error with {method}: {data['error']['message'] if isinstance(data['error'], dict) else data['error']}")
                    else:
                        print(f"  ? Different response with {method}: {data}")
                except json.JSONDecodeError:
                    print(f"  ✗ Response not valid JSON with {method}")
            else:
                print(f"  ✗ HTTP Error with {method}: {response.status_code}")
                
        except Exception as e:
            print(f"  ✗ Exception with {method}: {str(e)}")

if __name__ == "__main__":
    test_list_functions()