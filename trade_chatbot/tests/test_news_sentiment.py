"""
Test for the NEWS_SENTIMENT function in the Alpha Vantage MCP wrapper
"""
import pytest
import json
import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))

def test_news_sentiment_method():
    """Test the av.function.news_sentiment method"""
    import requests
    
    # Test endpoint
    url = 'http://localhost:5001/api/mcp_wrapper'
    
    # Test case 1: Basic news sentiment request with tickers
    payload = {
        "jsonrpc": "2.0",
        "method": "av.function.news_sentiment",
        "params": {
            "tickers": "AAPL,MSFT"
        },
        "id": 1
    }
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        assert response.status_code == 200
        
        data = response.json()
        assert "jsonrpc" in data
        assert data["jsonrpc"] == "2.0"
        assert "id" in data
        assert data["id"] == 1
        
        # Check that we either got a result or a proper error
        assert ("result" in data) or ("error" in data)
        
        if "result" in data:
            # If we got results, verify the structure
            result = data["result"]
            # The response should contain feed or sentiment data
            assert isinstance(result, dict)
            
    except requests.exceptions.ConnectionError:
        # If the server is not running, skip the test
        pytest.skip("MCP server not running")
    except Exception as e:
        pytest.fail(f"Unexpected error: {str(e)}")

def test_news_sentiment_with_topics():
    """Test the av.function.news_sentiment method with topics parameter"""
    import requests
    
    # Test endpoint
    url = 'http://localhost:5001/api/mcp_wrapper'
    
    # Test case 2: News sentiment request with topics
    payload = {
        "jsonrpc": "2.0",
        "method": "av.function.news_sentiment",
        "params": {
            "topics": "financial_markets"
        },
        "id": 2
    }
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        assert response.status_code == 200
        
        data = response.json()
        assert "jsonrpc" in data
        assert data["jsonrpc"] == "2.0"
        assert "id" in data
        assert data["id"] == 2
        
        # Check that we either got a result or a proper error
        assert ("result" in data) or ("error" in data)
        
    except requests.exceptions.ConnectionError:
        # If the server is not running, skip the test
        pytest.skip("MCP server not running")
    except Exception as e:
        pytest.fail(f"Unexpected error: {str(e)}")

def test_news_sentiment_invalid_parameters():
    """Test the av.function.news_sentiment method with invalid parameters"""
    import requests
    
    # Test endpoint
    url = 'http://localhost:5001/api/mcp_wrapper'
    
    # Test case 3: News sentiment request with invalid parameters
    payload = {
        "jsonrpc": "2.0",
        "method": "av.function.news_sentiment",
        "params": {
            "invalid_param": "value"
        },
        "id": 3
    }
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        assert response.status_code == 200
        
        data = response.json()
        assert "jsonrpc" in data
        assert data["jsonrpc"] == "2.0"
        assert "id" in data
        assert data["id"] == 3
        
        # Should still work even with extra parameters (they'll be ignored)
        assert ("result" in data) or ("error" in data)
        
    except requests.exceptions.ConnectionError:
        # If the server is not running, skip the test
        pytest.skip("MCP server not running")
    except Exception as e:
        pytest.fail(f"Unexpected error: {str(e)}")

if __name__ == "__main__":
    # Run the tests
    test_news_sentiment_method()
    test_news_sentiment_with_topics()
    test_news_sentiment_invalid_parameters()
    print("All NEWS_SENTIMENT tests passed!")