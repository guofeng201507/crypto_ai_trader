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

ALPHA_VANTAGE_API_KEY = os.environ.get('ALPHA_VANTAGE_API_KEY', '20KCRQCE82CTCDVI')
ALPHA_VANTAGE_BASE_URL = 'https://www.alphavantage.co/query'

def get_crypto_data(symbol: str, market: str = "USD") -> Optional[Dict]:
    """
    Get cryptocurrency data for a given symbol using Alpha Vantage API
    """
    logger.info(f"Fetching cryptocurrency data for symbol: {symbol}, market: {market}")
    
    try:
        # Using the digital currency listing function for Alpha Vantage
        params = {
            "function": "CURRENCY_EXCHANGE_RATE",
            "from_currency": symbol,
            "to_currency": market,
            "apikey": ALPHA_VANTAGE_API_KEY
        }
        
        logger.info(f"Making crypto API request to: {ALPHA_VANTAGE_BASE_URL} with params: {params}")
        
        response = requests.get(ALPHA_VANTAGE_BASE_URL, params=params)
        
        logger.info(f"Crypto API response status code: {response.status_code}")
        logger.info(f"Crypto API response text: {response.text}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                logger.info(f"Crypto API response data: {data}")
                
                # Check if the response contains the expected data
                if "Realtime Currency Exchange Rate" in data:
                    rate_info = data["Realtime Currency Exchange Rate"]
                    result = {
                        "symbol": rate_info.get("1. From_Currency Code"),
                        "market": rate_info.get("3. To_Currency Code"),
                        "price": float(rate_info.get("5. Exchange Rate", 0)),
                        "open": float(rate_info.get("8. Bid Price", 0)),
                        "high": float(rate_info.get("9. Ask Price", 0)),
                        "last_refreshed": rate_info.get("6. Last Refreshed"),
                        "timezone": rate_info.get("7. Time Zone"),
                        "summary": f"1 {rate_info.get('1. From_Currency Code', 'N/A')} = {rate_info.get('5. Exchange Rate', 'N/A')} {rate_info.get('3. To_Currency Code', 'N/A')}, "
                                   f"Bid: {rate_info.get('8. Bid Price', 'N/A')}, Ask: {rate_info.get('9. Ask Price', 'N/A')}"
                    }
                    
                    logger.info(f"Successfully parsed crypto data for {symbol}: {result}")
                    return result
                else:
                    # If the specific function isn't available, return None
                    logger.warning(f"Crypto data not available for symbol {symbol}: {data}")
                    return None
            except ValueError:
                # Handle case where response is not JSON
                logger.error(f"Crypto response is not valid JSON for symbol {symbol}: {response.text}")
                return None
        else:
            logger.error(f"Error fetching crypto data for {symbol}: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        logger.error(f"Exception occurred while fetching crypto data for {symbol}: {str(e)}")
        return None

def get_stock_data(symbol: str) -> Optional[Dict]:
    """
    Get data for a given symbol (stock or crypto) using Alpha Vantage API
    """
    logger.info(f"Fetching data for symbol: {symbol}")
    
    # Common cryptocurrency symbols that Alpha Vantage supports
    crypto_symbols = {"BTC", "ETH", "LTC", "BCH", "BNB", "EOS", "XRP", "XLM", "ADA", "TRX", "USDT", "DOT", "UNI"}
    
    # Check if the symbol is likely a cryptocurrency
    if symbol.upper() in crypto_symbols:
        logger.info(f"Detected cryptocurrency symbol: {symbol}, using crypto API")
        return get_crypto_data(symbol)
    
    try:
        # Using the regular Alpha Vantage API for stocks
        params = {
            "function": "GLOBAL_QUOTE",
            "symbol": symbol,
            "apikey": ALPHA_VANTAGE_API_KEY
        }
        
        logger.info(f"Making API request to: {ALPHA_VANTAGE_BASE_URL} with params: {params}")
        
        response = requests.get(ALPHA_VANTAGE_BASE_URL, params=params)
        
        logger.info(f"API response status code: {response.status_code}")
        logger.info(f"API response text: {response.text}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                logger.info(f"API response data: {data}")
                
                # Check if the response contains the expected data
                if "Global Quote" in data:
                    quote = data["Global Quote"]
                    result = {
                        "symbol": quote.get("01. symbol"),
                        "price": float(quote.get("05. price", 0)),
                        "open": float(quote.get("02. open", 0)),
                        "high": float(quote.get("03. high", 0)),
                        "low": float(quote.get("04. low", 0)),
                        "volume": int(quote.get("06. volume", 0)),
                        "latest_trading_day": quote.get("07. latest trading day"),
                        "previous_close": float(quote.get("08. previous close", 0)),
                        "change": float(quote.get("09. change", 0)),
                        "change_percent": quote.get("10. change percent"),
                        "summary": f"Price: ${quote.get('05. price', 'N/A')}, "
                                   f"Change: {quote.get('09. change', 'N/A')} "
                                   f"({quote.get('10. change percent', 'N/A')})"
                    }
                    
                    logger.info(f"Successfully parsed stock data for {symbol}: {result}")
                    return result
                else:
                    # If the specific function isn't available, return None
                    logger.warning(f"Data not available for symbol {symbol}: {data}")
                    return None
            except ValueError:
                # Handle case where response is not JSON
                logger.error(f"Response is not valid JSON for symbol {symbol}: {response.text}")
                return None
        else:
            logger.error(f"Error fetching data for {symbol}: {response.status_code} - {response.text}")
            # Try the crypto API if stock API fails
            crypto_result = get_crypto_data(symbol)
            if crypto_result:
                return crypto_result
            return None
    except Exception as e:
        logger.error(f"Exception occurred while fetching data for {symbol}: {str(e)}")
        # Try the crypto API if stock API fails with exception
        crypto_result = get_crypto_data(symbol)
        if crypto_result:
            return crypto_result
        return None

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