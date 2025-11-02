"""
Utility functions for the trade chatbot
"""
import requests
import os
from dotenv import load_dotenv
from typing import Dict, Optional
import logging
from datetime import datetime
import time

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# Import key manager for API key rotation
from .key_manager import (
    initialize_key_manager,
    get_current_key,
    rotate_key,
    mark_key_usage,
    is_rate_limited_response
)

# Initialize key manager with multiple API keys
api_keys = os.environ.get('ALPHA_VANTAGE_API_KEYS', '20KCRQCE82CTCDVI,8DW7GH8FIZDXGFHC').split(',')
api_keys = [key.strip() for key in api_keys if key.strip()]
initialize_key_manager(api_keys)

# Alpha Vantage configuration (keeping for backward compatibility)
ALPHA_VANTAGE_BASE_URL = 'https://www.alphavantage.co/query'

# Yahoo Finance configuration
YAHOO_FINANCE_BASE_URL = 'https://query1.finance.yahoo.com/v8/finance/chart/'

# Alpha Vantage MCP configuration
MCP_BASE_URL = 'http://localhost:5001/api/mcp_wrapper'

def format_asset_info(asset_data: Dict, symbol: str) -> str:
    """
    Format asset information into a concise string (under 150 words)
    """
    if not asset_data:
        return f"Sorry, I couldn't retrieve data for {symbol}."
    
    # Extract key information
    price = asset_data.get('price', 'N/A')
    change = asset_data.get('change', 'N/A')
    change_percent = asset_data.get('change_percent', 'N/A')
    volume = asset_data.get('volume', 'N/A')
    high = asset_data.get('high', 'N/A')
    low = asset_data.get('low', 'N/A')
    
    # Create a concise summary (aiming for under 150 words)
    if symbol.endswith('-USD') or symbol in ['BTC-USD', 'ETH-USD', 'XAUUSD', 'XAGUSD']:
        # Crypto or precious metals
        summary = f"{symbol}: ${price} "
        if change != 'N/A':
            summary += f"(Change: ${change} | {change_percent}%) "
        if volume != 'N/A' and volume != 0:
            summary += f"| Vol: {volume} "
        if high != 'N/A':
            summary += f"| High: ${high} | Low: ${low}"
    else:
        # Stocks
        summary = f"{symbol}: ${price} "
        if change != 'N/A':
            summary += f"(Change: ${change} | {change_percent}%) "
        if volume != 'N/A' and volume != 0:
            summary += f"| Vol: {volume:,} "
        if high != 'N/A':
            summary += f"| High: ${high} | Low: ${low}"
    
    # Ensure the summary is concise
    if len(summary) > 200:  # Allow some buffer
        summary = summary[:197] + "..."
        
    return summary

def format_stock_info(stock_data: Dict, symbol: str) -> str:
    """
    Format stock information into a concise string (under 150 words)
    """
    return format_asset_info(stock_data, symbol)

def format_crypto_info(crypto_data: Dict, symbol: str) -> str:
    """
    Format cryptocurrency information into a concise string (under 150 words)
    """
    return format_asset_info(crypto_data, symbol)

def format_precious_metal_info(metal_data: Dict, symbol: str) -> str:
    """
    Format precious metal information into a concise string (under 150 words)
    """
    return format_asset_info(metal_data, symbol)


def call_alpha_vantage_api_with_retry(function: str, max_retries: int = 3, **params) -> Optional[Dict]:
    """
    Call the Alpha Vantage API with automatic key rotation on rate limit errors
    
    Args:
        function: Alpha Vantage API function name
        max_retries: Maximum number of retries with different keys
        **params: Additional parameters for the API call
        
    Returns:
        API response data or None if all retries fail
    """
    for attempt in range(max_retries):
        # Get current API key
        api_key = get_current_key()
        logger.info(f"Calling Alpha Vantage API (attempt {attempt + 1}/{max_retries}) with key: {api_key[:5]}...")
        
        api_params = {
            'function': function,
            'apikey': api_key,
            **params
        }
        
        try:
            response = requests.get(ALPHA_VANTAGE_BASE_URL, params=api_params, timeout=30)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    
                    # Mark successful usage
                    mark_key_usage(api_key)
                    
                    # Check if we hit a rate limit
                    if is_rate_limited_response(data):
                        logger.warning(f"Rate limit detected with key {api_key[:5]}... on attempt {attempt + 1}")
                        if attempt < max_retries - 1:  # Not the last attempt
                            # Rotate to next key and try again
                            new_key = rotate_key()
                            logger.info(f"Rotating to next key: {new_key[:5]}...")
                            time.sleep(1)  # Brief pause before retry
                            continue
                        else:
                            logger.error("All API keys exhausted, rate limit still hit")
                            return data  # Return the rate limit response
                    else:
                        # Successful response
                        logger.info(f"Successful Alpha Vantage API call with key {api_key[:5]}...")
                        return data
                        
                except ValueError:
                    logger.error(f"Response from Alpha Vantage is not valid JSON: {response.text}")
                    if attempt < max_retries - 1:
                        rotate_key()
                        time.sleep(1)
                        continue
                    else:
                        return None
            else:
                logger.error(f"Error from Alpha Vantage API: {response.status_code} - {response.text}")
                if attempt < max_retries - 1:
                    rotate_key()
                    time.sleep(1)
                    continue
                else:
                    return None
                    
        except requests.exceptions.Timeout:
            logger.error(f"Timeout calling Alpha Vantage API with key {api_key[:5]}...")
            if attempt < max_retries - 1:
                rotate_key()
                time.sleep(2)  # Longer pause for timeout
                continue
            else:
                return None
        except Exception as e:
            logger.error(f"Exception calling Alpha Vantage API with key {api_key[:5]}...: {str(e)}")
            if attempt < max_retries - 1:
                rotate_key()
                time.sleep(1)
                continue
            else:
                return None
    
    return None

def call_alpha_vantage_api(function: str, **params) -> Optional[Dict]:
    """
    Call the Alpha Vantage API with the given function and parameters
    """
    return call_alpha_vantage_api_with_retry(function, **params)

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
        # Using the Alpha Vantage API with key rotation
        result = call_alpha_vantage_api(
            "TIME_SERIES_DAILY",
            symbol=symbol,
            outputsize=outputsize,  # "compact" (last 100 days) or "full" (20+ years)
            datatype=datatype
        )
        
        if result:
            logger.info(f"Successfully fetched historical data for {symbol}")
            # Check if the response contains the expected data
            if "Time Series (Daily)" in result:
                return result
            else:
                logger.warning(f"Historical data not available for symbol {symbol}: {result}")
                return None
        else:
            logger.error(f"Failed to fetch historical data for {symbol}")
            return None
            
    except Exception as e:
        logger.error(f"Exception occurred while fetching historical data for {symbol}: {str(e)}")
        return None


def get_mcp_data(symbol: str) -> Optional[Dict]:
    """
    Get stock data using our own MCP wrapper for Alpha Vantage API
    This implements the Model Context Protocol (MCP) to wrap the standard Alpha Vantage API
    """
    import json
    logger.info(f"Fetching data for symbol: {symbol} from our Alpha Vantage MCP wrapper")
    
    # Use our own MCP wrapper endpoint instead of the external one
    mcp_url = "http://localhost:5001/api/mcp_wrapper"
    
    # Define the method to call in our MCP wrapper
    method = "av.function.global_quote"
    
    headers = {
        "Content-Type": "application/json"
    }
    
    # Prepare the JSON-RPC request
    payload = {
        "jsonrpc": "2.0",
        "method": method,
        "params": {
            "symbol": symbol
        },
        "id": 1
    }
    
    try:
        logger.info(f"Making JSON-RPC request to our MCP wrapper: {mcp_url}")
        logger.info(f"Payload: {payload}")
        
        response = requests.post(
            mcp_url,
            json=payload,
            headers=headers,
            timeout=30
        )
        
        logger.info(f"MCP wrapper response status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                logger.info(f"MCP wrapper response: {data}")
                
                if "result" in data:
                    # Return the raw result for further processing
                    result_data = {
                        "symbol": symbol,
                        "raw_data": data["result"],
                        "source": "mcp"
                    }
                    
                    # Try to extract standard fields if available
                    if "Global Quote" in data["result"]:
                        quote_data = data["result"]["Global Quote"]
                        result_data.update({
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
                        })
                    elif "Time Series (Daily)" in data["result"]:
                        # Extract latest daily data
                        time_series = data["result"]["Time Series (Daily)"]
                        latest_date = sorted(time_series.keys())[-1]  # Most recent date
                        latest_data = time_series[latest_date]
                        result_data.update({
                            "symbol": data["result"].get("Meta Data", {}).get("2. Symbol", symbol),
                            "price": float(latest_data.get("4. close", 0)),
                            "open": float(latest_data.get("1. open", 0)),
                            "high": float(latest_data.get("2. high", 0)),
                            "low": float(latest_data.get("3. low", 0)),
                            "volume": int(latest_data.get("5. volume", 0)),
                            "latest_trading_day": latest_date
                        })
                    else:
                        # If the result is directly the quote data (without "Global Quote" wrapper)
                        # This follows the same format as the standard API response
                        result_data.update({
                            "symbol": data["result"].get("01. symbol", symbol),
                            "price": float(data["result"].get("05. price", 0)),
                            "open": float(data["result"].get("02. open", 0)),
                            "high": float(data["result"].get("03. high", 0)),
                            "low": float(data["result"].get("04. low", 0)),
                            "volume": int(data["result"].get("06. volume", 0)),
                            "latest_trading_day": data["result"].get("07. latest trading day", ""),
                            "previous_close": float(data["result"].get("08. previous close", 0)),
                            "change": float(data["result"].get("09. change", 0)),
                            "change_percent": data["result"].get("10. change percent", "0%"),
                            "summary": f"Price: ${data['result'].get('05. price', 'N/A')} "
                                      f"Change: {data['result'].get('09. change', 'N/A')} "
                                      f"({data['result'].get('10. change percent', 'N/A')})"
                        })
                    
                    logger.info(f"Successfully parsed MCP data for {symbol}: {result_data}")
                    return result_data
                elif "error" in data:
                    logger.error(f"MCP wrapper returned error: {data['error']}")
                    return None
                else:
                    logger.warning(f"Unexpected response format from MCP wrapper: {data}")
                    return None
            except json.JSONDecodeError:
                logger.error(f"Response from MCP wrapper is not valid JSON: {response.text}")
                return None
        else:
            logger.error(f"HTTP Error from MCP wrapper: {response.status_code} - {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Network error calling MCP wrapper: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error calling MCP wrapper: {str(e)}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        return None