"""
Test script for Trade Chatbot APIs
This script allows testing of both Alpha Vantage and Qwen APIs independently.
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

def test_alpha_vantage_api():
    """Test the Alpha Vantage API directly"""
    print("\n=== Testing Alpha Vantage API ===")
    
    api_key = os.environ.get('ALPHA_VANTAGE_API_KEY', '20KCRQCE82CTCDVI')
    if not api_key or api_key == '20KCRQCE82CTCDVI':
        print("WARNING: Using default API key. Consider setting your own ALPHA_VANTAGE_API_KEY in .env")
    
    # Test with a valid symbol
    symbols_to_test = ['AAPL'] # 'GOOGL', 'MSFT', 'TSLA'
    
    for symbol in symbols_to_test:
        print(f"\nTesting symbol: {symbol}")
        
        # Using the MCP server
        mcp_url = 'https://mcp.alphavantage.co/mcp'
        params = {
            'apikey': api_key,
            'function': 'GLOBAL_QUOTE',
            'symbol': symbol
        }
        
        try:
            response = requests.get(mcp_url, params=params, timeout=30)
            logger.info(f"Alpha Vantage API response status for {symbol}: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Alpha Vantage API response for {symbol}: {data}")
                
                if "Global Quote" in data:
                    quote = data["Global Quote"]
                    print(f"  ✓ Successfully retrieved data for {symbol}")
                    print(f"    Price: {quote.get('05. price', 'N/A')}")
                    print(f"    Change: {quote.get('09. change', 'N/A')} ({quote.get('10. change percent', 'N/A')})")
                else:
                    print(f"  ✗ No 'Global Quote' in response for {symbol}")
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
        symbols = ['AAPL', 'GOOGL']
        for symbol in symbols:
            print(f"\nTesting stock data for {symbol}:")
            stock_data = get_stock_data(symbol)
            if stock_data:
                print(f"  ✓ Got stock data: {stock_data}")
            else:
                print(f"  ✗ Failed to get stock data for {symbol}")
        
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
    print("This script will test both the Alpha Vantage and Qwen APIs")
    
    # Run all tests
    test_alpha_vantage_api()
    test_qwen_api()
    test_integration()
    
    print("\n=== Testing Complete ===")
    print("Check the logs above to see the results of each test")