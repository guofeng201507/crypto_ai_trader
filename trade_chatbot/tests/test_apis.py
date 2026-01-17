"""
Test script for Trade Chatbot APIs
This script allows testing of both Yahoo Finance and Qwen APIs independently.
"""
import os
import sys
import requests
from dotenv import load_dotenv
import logging

# Add the project root to the path so imports work
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_yahoo_finance_api():
    """Test the Yahoo Finance API directly"""
    print("\n=== Testing Yahoo Finance API ===")
    
    # Test with a valid symbol
    symbols_to_test = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'BTC-USD', 'ETH-USD']
    
    for symbol in symbols_to_test:
        print(f"\nTesting symbol: {symbol}")
        
        try:
            # Using the Yahoo Finance base URL
            yahoo_url = 'https://query1.finance.yahoo.com/v8/finance/chart/' + symbol
            
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            
            params = {
                "range": "1d",
                "interval": "1m"
            }
            
            response = requests.get(yahoo_url, params=params, headers=headers, timeout=30)
            logger.info(f"Yahoo Finance API response status for {symbol}: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Yahoo Finance API response keys for {symbol}: {list(data.keys())}")
                
                if "chart" in data and "result" in data["chart"] and len(data["chart"]["result"]) > 0:
                    result = data["chart"]["result"][0]
                    meta = result.get("meta", {})
                    print(f"  ✓ Successfully retrieved data for {symbol}")
                    print(f"    Symbol: {meta.get('symbol', 'N/A')}")
                    print(f"    Price: ${meta.get('regularMarketPrice', 'N/A')}")
                    print(f"    Previous Close: ${meta.get('previousClose', 'N/A')}")
                else:
                    print(f"  ✗ No chart data in response for {symbol}")
                    print(f"    Response keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
            else:
                print(f"  ✗ Error fetching data for {symbol}: {response.status_code}")
                print(f"    Response: {response.text}")
                
        except Exception as e:
            print(f"  ✗ Exception fetching data for {symbol}: {str(e)}")

def test_qwen_api():
    """Test the Qwen API directly"""
    print("\n=== Testing Qwen API ===")
    
    api_key = os.environ.get('QWEN_API_KEY')
    base_url = os.environ.get('QWEN_BASE_URL', 'https://dashscope.aliyuncs.com/compatible-mode/v1')
    
    if not api_key:
        print("ERROR: QWEN_API_KEY not found in environment variables")
        return
    
    # Test with a simple prompt
    test_prompt = "Hello, how are you? This is a test of the Qwen API."
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    payload = {
        "model": "qwen-max",  # You can change this to other available models
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": test_prompt}
        ],
        "max_tokens": 200,
        "temperature": 0.7
    }
    
    try:
        print(f"Making request to: {base_url}/chat/completions")
        response = requests.post(
            f"{base_url}/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        logger.info(f"Qwen API response status: {response.status_code}")
        
        if response.status_code == 200:
            response_data = response.json()
            content = response_data['choices'][0]['message']['content']
            print("  ✓ Successfully received response from Qwen API")
            print(f"  Response: {content}")
        else:
            print(f"  ✗ Error calling Qwen API: {response.status_code}")
            print(f"  Response: {response.text}")
            
    except Exception as e:
        print(f"  ✗ Exception calling Qwen API: {str(e)}")

def test_integration():
    """Test the integration of both APIs as used in the chatbot"""
    print("\n=== Testing API Integration (as used in chatbot) ===")
    
    # Import the helper function to test it directly
    try:
        from trade_chatbot.backend.utils.helpers import get_stock_data
        from trade_chatbot.backend.api.chat import generate_response_with_qwen
        
        # Test stock data retrieval
        symbols = ['AAPL', 'GOOGL', 'BTC-USD', 'ETH-USD']
        for symbol in symbols:
            print(f"\nTesting data for {symbol}:")
            stock_data = get_stock_data(symbol)
            if stock_data:
                print(f"  ✓ Got data: {stock_data}")
            else:
                print(f"  ✗ Failed to get data for {symbol}")
        
        # Test AI response generation (without stock data)
        print(f"\nTesting Qwen response generation:")
        test_message = "What is the current market trend?"
        context = []  # Empty context for this test
        response = generate_response_with_qwen(test_message, context)
        print(f"  Response: {response}")
        
    except ImportError as e:
        print(f"Import error: {e}")
        print("Make sure you're running this from the project root directory")
    except Exception as e:
        print(f"Integration test error: {e}")

if __name__ == "__main__":
    print("Trade Chatbot API Testing Tool")
    print("This script will test both the Yahoo Finance and Qwen APIs")
    
    # Run all tests
    test_yahoo_finance_api()
    test_qwen_api()
    test_integration()
    
    print("\n=== Testing Complete ===")
    print("Check the logs above to see the results of each test")