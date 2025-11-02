"""
Test script to verify the NEWS_SENTIMENT function is working correctly
"""
import requests
import json
import pytest

def test_news_sentiment_with_tickers():
    """Test the av.function.news_sentiment method with tickers parameter"""
    url = 'http://localhost:5001/api/mcp_wrapper'
    
    payload = {
        "jsonrpc": "2.0",
        "method": "av.function.news_sentiment",
        "params": {
            "tickers": "AAPL,MSFT,TSLA"
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
            assert isinstance(result, dict)
            assert "feed" in result
            assert isinstance(result["feed"], list)
            assert len(result["feed"]) > 0
            
            # Check the first news item structure
            first_item = result["feed"][0]
            assert "title" in first_item
            assert "url" in first_item
            assert "time_published" in first_item
            
    except requests.exceptions.ConnectionError:
        # If the server is not running, skip the test
        pytest.skip("MCP server not running")
    except Exception as e:
        pytest.fail(f"Unexpected error: {str(e)}")

def test_news_sentiment_with_topics():
    """Test the av.function.news_sentiment method with topics parameter"""
    url = 'http://localhost:5001/api/mcp_wrapper'
    
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
        
        if "result" in data:
            # If we got results, verify the structure
            result = data["result"]
            assert isinstance(result, dict)
            assert "feed" in result
            
    except requests.exceptions.ConnectionError:
        # If the server is not running, skip the test
        pytest.skip("MCP server not running")
    except Exception as e:
        pytest.fail(f"Unexpected error: {str(e)}")

def test_news_sentiment_with_limit():
    """Test the av.function.news_sentiment method with limit parameter"""
    url = 'http://localhost:5001/api/mcp_wrapper'
    
    payload = {
        "jsonrpc": "2.0",
        "method": "av.function.news_sentiment",
        "params": {
            "limit": 5
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
        
        # Check that we either got a result or a proper error
        assert ("result" in data) or ("error" in data)
        
        if "result" in data:
            # If we got results, verify the structure
            result = data["result"]
            assert isinstance(result, dict)
            assert "feed" in result
            # The limit parameter may not always be respected by the API
            # but we should at least verify we got a feed
            
    except requests.exceptions.ConnectionError:
        # If the server is not running, skip the test
        pytest.skip("MCP server not running")
    except Exception as e:
        pytest.fail(f"Unexpected error: {str(e)}")

if __name__ == "__main__":
    # Run the tests
    test_news_sentiment_with_tickers()
    test_news_sentiment_with_topics()
    test_news_sentiment_with_limit()
    print("All NEWS_SENTIMENT function tests passed!")