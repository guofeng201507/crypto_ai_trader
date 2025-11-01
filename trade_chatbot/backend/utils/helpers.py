"""
Utility functions for the trade chatbot
"""
import requests
import os
from dotenv import load_dotenv
from typing import Dict, Optional
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# Alpha Vantage configuration (keeping for backward compatibility)
ALPHA_VANTAGE_API_KEY = os.environ.get('ALPHA_VANTAGE_API_KEY', '20KCRQCE82CTCDVI')
ALPHA_VANTAGE_BASE_URL = 'https://www.alphavantage.co/query'

# Yahoo Finance configuration
YAHOO_FINANCE_BASE_URL = 'https://query1.finance.yahoo.com/v8/finance/chart/'

# Alpha Vantage MCP configuration
MCP_BASE_URL = 'https://mcp.alphavantage.co/mcp'

def get_yahoo_finance_data(symbol: str) -> Optional[Dict]:
    """
    Get stock or cryptocurrency data for a given symbol using Yahoo Finance API
    """
    logger.info(f"Fetching data for symbol: {symbol} from Yahoo Finance")
    
    try:
        # Using Yahoo Finance API
        url = f"{YAHOO_FINANCE_BASE_URL}{symbol}"
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        params = {
            "range": "1d",
            "interval": "1m"
        }
        
        logger.info(f"Making Yahoo Finance API request to: {url} with params: {params}")
        
        response = requests.get(url, params=params, headers=headers)
        
        logger.info(f"Yahoo Finance API response status code: {response.status_code}")
        logger.info(f"Yahoo Finance API response text: {response.text[:200]}...")  # Log first 200 chars
        
        if response.status_code == 200:
            try:
                data = response.json()
                logger.info(f"Yahoo Finance API response data keys: {list(data.keys())}")
                
                # Check if the response contains the expected data
                if "chart" in data and "result" in data["chart"] and len(data["chart"]["result"]) > 0:
                    result = data["chart"]["result"][0]
                    
                    # Extract metadata
                    meta = result.get("meta", {})
                    
                    # Extract the latest quote data
                    if "indicators" in result and "quote" in result["indicators"] and len(result["indicators"]["quote"]) > 0:
                        quote = result["indicators"]["quote"][0]
                        
                        # Get the latest non-null values
                        latest_index = -1
                        latest_price = None
                        latest_volume = None
                        
                        # Find the latest valid data point
                        for i in range(len(quote.get("close", [])) - 1, -1, -1):
                            if quote.get("close", [])[i] is not None:
                                latest_index = i
                                latest_price = float(quote.get("close", [])[i])
                                latest_volume = int(quote.get("volume", [])[i] or 0)
                                break
                        
                        if latest_price is not None:
                            result_data = {
                                "symbol": meta.get("symbol"),
                                "price": latest_price,
                                "open": float(meta.get("previousClose", 0)),
                                "high": float(max([x for x in quote.get("high", []) if x is not None]) if quote.get("high") else 0),
                                "low": float(min([x for x in quote.get("low", []) if x is not None]) if quote.get("low") else 0),
                                "volume": latest_volume,
                                "latest_trading_day": datetime.fromtimestamp(meta.get("regularMarketTime", 0)).strftime('%Y-%m-%d'),
                                "previous_close": float(meta.get("previousClose", 0)),
                                "change": latest_price - float(meta.get("previousClose", 0)),
                                "change_percent": ((latest_price - float(meta.get("previousClose", 0))) / float(meta.get("previousClose", 1)) * 100) if meta.get("previousClose") else 0,
                                "summary": f"Price: ${latest_price:.2f}, "
                                           f"Change: ${latest_price - float(meta.get('previousClose', 0)):.2f} "
                                           f"({((latest_price - float(meta.get('previousClose', 0))) / float(meta.get('previousClose', 1)) * 100):.2f}%)"
                            }
                            
                            logger.info(f"Successfully parsed Yahoo Finance data for {symbol}: {result_data}")
                            return result_data
                        else:
                            logger.warning(f"No valid price data found for symbol {symbol}")
                            return None
                    else:
                        logger.warning(f"No quote data available for symbol {symbol}: {result}")
                        return None
                else:
                    # If the specific function isn't available, return None
                    logger.warning(f"Data not available for symbol {symbol}: {data}")
                    return None
            except ValueError as ve:
                # Handle case where response is not JSON
                logger.error(f"Yahoo Finance response is not valid JSON for symbol {symbol}: {response.text}")
                logger.error(f"ValueError: {str(ve)}")
                return None
            except Exception as je:
                # Handle JSON parsing errors
                logger.error(f"Error parsing Yahoo Finance JSON for symbol {symbol}: {str(je)}")
                return None
        else:
            logger.error(f"Error fetching data from Yahoo Finance for {symbol}: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        logger.error(f"Exception occurred while fetching data from Yahoo Finance for {symbol}: {str(e)}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        return None

def get_crypto_data(symbol: str, market: str = "USD") -> Optional[Dict]:
    """
    Get cryptocurrency data for a given symbol using Yahoo Finance API
    Convert common crypto symbols to Yahoo Finance format (e.g., BTC -> BTC-USD)
    """
    logger.info(f"Fetching cryptocurrency data for symbol: {symbol}, market: {market}")
    
    # Convert symbol to Yahoo Finance format
    if "-USD" in symbol or "-BTC" in symbol or "-ETH" in symbol or "-EUR" in symbol or "-GBP" in symbol:
        # Already in the correct format (e.g., BTC-USD)
        yahoo_symbol = symbol
    else:
        # Need to format it (e.g., BTC to BTC-USD)
        yahoo_symbol = f"{symbol}-{market}"
    
    return get_yahoo_finance_data(yahoo_symbol)

def get_stock_data(symbol: str) -> Optional[Dict]:
    """
    Get data for a given symbol (stock, crypto, or precious metals) using Yahoo Finance API as primary and MCP as fallback
    """
    logger.info(f"Fetching data for symbol: {symbol}")
    
    # Common cryptocurrency symbols that Yahoo Finance supports
    crypto_symbols = {"BTC", "ETH", "LTC", "BCH", "BNB", "EOS", "XRP", "XLM", "ADA", "TRX", "USDT", "DOT", "UNI"}
    
    # Precious metals and forex symbols that Yahoo Finance supports
    precious_metals = {"XAUUSD", "XAGUSD", "XPTUSD", "XPDUSD"}
    
    symbol_upper = symbol.upper()
    
    # Handle precious metals symbols (e.g., XAUUSD, XAGUSD, etc.)
    if symbol_upper in precious_metals:
        logger.info(f"Detected precious metal symbol: {symbol}, using Yahoo Finance API directly")
        yahoo_result = get_yahoo_finance_data(symbol_upper)
        if yahoo_result:
            return yahoo_result
        else:
            # Fallback to MCP server if Yahoo Finance fails
            logger.info(f"Yahoo Finance failed for {symbol}, trying MCP server as fallback")
            return get_mcp_data(symbol_upper)
    
    # Check if it's a crypto symbol in the form BTC-USD, ETH-USD, etc.
    if '-' in symbol_upper and symbol_upper.split('-')[0] in crypto_symbols:
        logger.info(f"Detected cryptocurrency symbol in format: {symbol}, using crypto API")
        result = get_crypto_data(symbol_upper.split('-')[0], symbol_upper.split('-')[1])  # Extract base and quote currencies
        if result:
            return result
        else:
            # Fallback to MCP server if Yahoo Finance fails
            logger.info(f"Crypto data failed for {symbol}, trying MCP server as fallback")
            return get_mcp_data(symbol_upper.split('-')[0])  # Use just the base currency for MCP
    
    # Check if the symbol is likely a cryptocurrency in short format (e.g., BTC, ETH)
    if symbol_upper in crypto_symbols:
        logger.info(f"Detected cryptocurrency symbol: {symbol}, using crypto API")
        result = get_crypto_data(symbol_upper)
        if result:
            return result
        else:
            # Fallback to MCP server
            logger.info(f"Crypto data failed for {symbol}, trying MCP server as fallback")
            return get_mcp_data(symbol_upper)
    
    # For stocks and other symbols, use Yahoo Finance as primary
    try:
        logger.info(f"Using Yahoo Finance API for symbol: {symbol}")
        yahoo_result = get_yahoo_finance_data(symbol_upper)
        if yahoo_result:
            return yahoo_result
        else:
            # Fallback to MCP server if Yahoo Finance fails
            logger.info(f"Yahoo Finance failed for {symbol}, trying MCP server as fallback")
            return get_mcp_data(symbol_upper)
    except Exception as e:
        logger.error(f"Exception occurred while fetching data for {symbol} from Yahoo Finance: {str(e)}")
        # Fallback to MCP server if Yahoo Finance fails
        logger.info(f"Trying MCP server as fallback for {symbol}")
        return get_mcp_data(symbol_upper)

def get_historical_data(symbol: str, outputsize: str = "compact", datatype: str = "json") -> Optional[Dict]:
    """
    Get historical stock data for a given symbol
    """
    logger.info(f"Fetching historical data for symbol: {symbol}, outputsize: {outputsize}")
    
    try:
        # Using the regular Alpha Vantage API
        params = {
            "function": "TIME_SERIES_DAILY",
            "symbol": symbol,
            "outputsize": outputsize,  # "compact" (last 100 days) or "full" (20+ years)
            "datatype": datatype,
            "apikey": ALPHA_VANTAGE_API_KEY
        }
        
        logger.info(f"Making historical API request to: {ALPHA_VANTAGE_BASE_URL} with params: {params}")
        
        response = requests.get(ALPHA_VANTAGE_BASE_URL, params=params)
        
        logger.info(f"Historical API response status code: {response.status_code}")
        logger.info(f"Historical API response text: {response.text}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                logger.info(f"Received historical data keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                
                # Check if the response contains the expected data
                if "Time Series (Daily)" in data:
                    logger.info(f"Successfully fetched historical data for {symbol}")
                    return data
                else:
                    # If the specific function isn't available, return None
                    logger.warning(f"Historical data not available for symbol {symbol}: {data}")
                    return None
            except ValueError:
                # Handle case where response is not JSON
                logger.error(f"Historical response is not valid JSON for symbol {symbol}: {response.text}")
                return None
        else:
            logger.error(f"Error fetching historical data for {symbol}: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        logger.error(f"Exception occurred while fetching historical data for {symbol}: {str(e)}")
        return None


def get_mcp_data(symbol: str) -> Optional[Dict]:
    """
    Get stock data using the Alpha Vantage MCP server
    """
    import json
    logger.info(f"Fetching data for symbol: {symbol} from Alpha Vantage MCP server")
    
    api_key = os.environ.get('ALPHA_VANTAGE_API_KEY', '20KCRQCE82CTCDVI')
    mcp_url = MCP_BASE_URL
    
    # Prepare the JSON-RPC request
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
        logger.info(f"Payload: {payload}")
        
        response = requests.post(
            mcp_url,
            json=payload,
            headers=headers,
            timeout=30
        )
        
        logger.info(f"MCP server response status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                logger.info(f"MCP server response: {data}")
                
                if "result" in data:
                    # Convert Alpha Vantage format to our standard format
                    quote_data = data["result"].get("Global Quote", {})
                    if quote_data:
                        result_data = {
                            "symbol": quote_data.get("01. symbol"),
                            "price": float(quote_data.get("05. price", 0)),
                            "open": float(quote_data.get("02. open", 0)),
                            "high": float(quote_data.get("03. high", 0)),
                            "low": float(quote_data.get("04. low", 0)),
                            "volume": int(quote_data.get("06. volume", 0)),
                            "latest_trading_day": quote_data.get("07. latest trading day"),
                            "previous_close": float(quote_data.get("08. previous close", 0)),
                            "change": float(quote_data.get("09. change", 0)),
                            "change_percent": quote_data.get("10. change percent", "0%").replace("%", ""),
                            "summary": f"Price: ${quote_data.get('05. price', 'N/A')} "
                                      f"Change: {quote_data.get('09. change', 'N/A')} "
                                      f"({quote_data.get('10. change percent', 'N/A')})"
                        }
                        logger.info(f"Successfully parsed MCP data for {symbol}: {result_data}")
                        return result_data
                elif "error" in data:
                    logger.error(f"MCP server error: {data['error']}")
                    return None
                else:
                    logger.warning(f"Unexpected response format from MCP server: {data}")
                    return None
            except json.JSONDecodeError:
                logger.error(f"Response from MCP server is not valid JSON: {response.text}")
                return None
        else:
            logger.error(f"HTTP Error from MCP server: {response.status_code} - {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Network error calling MCP server: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error calling MCP server for {symbol}: {str(e)}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        return None