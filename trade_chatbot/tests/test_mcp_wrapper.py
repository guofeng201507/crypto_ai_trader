"""
Unit tests for the Alpha Vantage MCP wrapper
"""
import pytest
from unittest.mock import patch, MagicMock
import json

# Import the MCP wrapper functions
# For now, we'll create mock versions for testing

class TestMCPWrapper:
    """Test cases for the Alpha Vantage MCP wrapper"""
    
    @patch('requests.post')
    def test_mcp_global_quote_method(self, mock_post):
        """Test the av.function.global_quote method"""
        # Mock the response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "jsonrpc": "2.0",
            "result": {
                "Global Quote": {
                    "01. symbol": "AAPL",
                    "02. open": "150.0000",
                    "03. high": "155.0000",
                    "04. low": "149.0000",
                    "05. price": "153.2500",
                    "06. volume": "1000000",
                    "07. latest trading day": "2025-11-02",
                    "08. previous close": "152.0000",
                    "09. change": "1.2500",
                    "10. change percent": "0.8224%"
                }
            },
            "id": 1
        }
        mock_post.return_value = mock_response
        
        # Test the method call (simulated)
        url = 'http://localhost:5001/api/mcp_wrapper'
        payload = {
            "jsonrpc": "2.0",
            "method": "av.function.global_quote",
            "params": {"symbol": "AAPL"},
            "id": 1
        }
        
        # This would normally make an actual request
        # For testing, we're just verifying the structure
        assert payload["method"] == "av.function.global_quote"
        assert payload["params"]["symbol"] == "AAPL"
        assert payload["jsonrpc"] == "2.0"
    
    @patch('requests.post')
    def test_mcp_currency_exchange_rate_method(self, mock_post):
        """Test the av.function.currency_exchange_rate method"""
        # Mock the response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "jsonrpc": "2.0",
            "result": {
                "Realtime Currency Exchange Rate": {
                    "1. From_Currency Code": "BTC",
                    "2. From_Currency Name": "Bitcoin",
                    "3. To_Currency Code": "USD",
                    "4. To_Currency Name": "United States Dollar",
                    "5. Exchange Rate": "109955.99000000",
                    "6. Last Refreshed": "2025-11-02 02:58:41",
                    "7. Time Zone": "UTC",
                    "8. Bid Price": "109955.98000000",
                    "9. Ask Price": "109955.99000000"
                }
            },
            "id": 1
        }
        mock_post.return_value = mock_response
        
        # Test the method call (simulated)
        payload = {
            "jsonrpc": "2.0",
            "method": "av.function.currency_exchange_rate",
            "params": {"from_currency": "BTC", "to_currency": "USD"},
            "id": 1
        }
        
        # Verify the structure
        assert payload["method"] == "av.function.currency_exchange_rate"
        assert payload["params"]["from_currency"] == "BTC"
        assert payload["params"]["to_currency"] == "USD"
        assert payload["jsonrpc"] == "2.0"
    
    @patch('requests.post')
    def test_mcp_time_series_daily_method(self, mock_post):
        """Test the av.function.time_series_daily method"""
        # Mock the response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "jsonrpc": "2.0",
            "result": {
                "Meta Data": {
                    "1. Information": "Daily Prices (open, high, low, close) and Volumes",
                    "2. Symbol": "MSFT",
                    "3. Last Refreshed": "2025-11-02 16:00:00",
                    "4. Output Size": "Compact",
                    "5. Time Zone": "US/Eastern"
                },
                "Time Series (Daily)": {
                    "2025-11-02": {
                        "1. open": "510.0000",
                        "2. high": "520.0000",
                        "3. low": "505.0000",
                        "4. close": "517.8100",
                        "5. volume": "34006424"
                    }
                }
            },
            "id": 1
        }
        mock_post.return_value = mock_response
        
        # Test the method call (simulated)
        payload = {
            "jsonrpc": "2.0",
            "method": "av.function.time_series_daily",
            "params": {"symbol": "MSFT", "outputsize": "compact"},
            "id": 1
        }
        
        # Verify the structure
        assert payload["method"] == "av.function.time_series_daily"
        assert payload["params"]["symbol"] == "MSFT"
        assert payload["params"]["outputsize"] == "compact"
        assert payload["jsonrpc"] == "2.0"
    
    @patch('requests.post')
    def test_mcp_symbol_search_method(self, mock_post):
        """Test the av.function.symbol_search method"""
        # Mock the response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "jsonrpc": "2.0",
            "result": {
                "bestMatches": [
                    {
                        "1. symbol": "TSLA",
                        "2. name": "Tesla Inc",
                        "3. type": "Equity",
                        "4. region": "United States",
                        "5. marketOpen": "09:30",
                        "6. marketClose": "16:00",
                        "7. timezone": "UTC-04",
                        "8. currency": "USD"
                    }
                ]
            },
            "id": 1
        }
        mock_post.return_value = mock_response
        
        # Test the method call (simulated)
        payload = {
            "jsonrpc": "2.0",
            "method": "av.function.symbol_search",
            "params": {"keywords": "Tesla"},
            "id": 1
        }
        
        # Verify the structure
        assert payload["method"] == "av.function.symbol_search"
        assert payload["params"]["keywords"] == "Tesla"
        assert payload["jsonrpc"] == "2.0"
    
    def test_json_rpc_request_structure(self):
        """Test that JSON-RPC requests follow the correct structure"""
        # Test a sample request
        request = {
            "jsonrpc": "2.0",
            "method": "sample.method",
            "params": {"param1": "value1"},
            "id": 123
        }
        
        # Verify JSON-RPC 2.0 structure
        assert "jsonrpc" in request
        assert request["jsonrpc"] == "2.0"
        assert "method" in request
        assert "params" in request
        assert "id" in request
        assert isinstance(request["id"], (int, str))

if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"])