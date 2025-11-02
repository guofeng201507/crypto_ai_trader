"""
MCP (Model Context Protocol) server wrapper for Alpha Vantage API
This module provides an MCP-compatible interface that wraps the standard Alpha Vantage API

Supported MCP Methods:
---------------------
1. av.function.global_quote
   - Get real-time quote data for stocks, ETFs, mutual funds, etc.
   - Parameters: symbol (required)
   
2. av.function.time_series_daily
   - Get daily time series data (open, high, low, close, volume)
   - Parameters: symbol (required), outputsize (optional)
   
3. av.function.symbol_search
   - Search for stock symbols by keywords
   - Parameters: keywords (required)
   
4. av.function.currency_exchange_rate
   - Get real-time exchange rates between currencies
   - Parameters: from_currency (required), to_currency (optional)
   
5. av.function.crypto_overview
   - Get cryptocurrency exchange rates
   - Parameters: symbol (required), market (optional)
   
6. av.function.news_sentiment
   - Get live news sentiment and anomaly detection
   - Parameters: tickers (optional), topics (optional), time_from (optional), 
                time_to (optional), sort (optional), limit (optional)

All methods follow JSON-RPC 2.0 specification with automatic key rotation
for rate limit protection.
"""
import requests
import os
from flask import Blueprint, request, jsonify
from dotenv import load_dotenv
import logging
import json
import time
from typing import Optional, Dict

# Load environment variables
load_dotenv()

# Import key manager for API key rotation
from ..utils.key_manager import (
    initialize_key_manager,
    get_current_key,
    rotate_key,
    mark_key_usage,
    is_rate_limited_response
)

logger = logging.getLogger(__name__)

# Configure Alpha Vantage API
ALPHA_VANTAGE_BASE_URL = 'https://www.alphavantage.co/query'

# Initialize key manager with multiple API keys
api_keys = os.environ.get('ALPHA_VANTAGE_API_KEYS', '20KCRQCE82CTCDVI,8DW7GH8FIZDXGFHC').split(',')
api_keys = [key.strip() for key in api_keys if key.strip()]
initialize_key_manager(api_keys)

# Create the MCP wrapper blueprint
mcp_wrapper_bp = Blueprint('mcp_wrapper', __name__)

def call_standard_alpha_vantage_api_with_retry(function, max_retries=3, **params):
    """
    Call the standard Alpha Vantage API with the given function and parameters
    with automatic key rotation on rate limit errors
    
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
        logger.info(f"Attempt {attempt + 1}/{max_retries} with API key: {api_key[:5]}...")
        
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
                        logger.info(f"Successful API call with key {api_key[:5]}...")
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

def call_standard_alpha_vantage_api(function, **params):
    """
    Call the standard Alpha Vantage API with the given function and parameters
    """
    return call_standard_alpha_vantage_api_with_retry(function, **params)

@mcp_wrapper_bp.route('/', methods=['POST'])
def mcp_handler():
    """
    MCP server endpoint that handles JSON-RPC requests for Alpha Vantage data
    """
    try:
        # Parse the JSON-RPC request
        request_data = request.get_json()
        
        if not request_data:
            return jsonify({
                "jsonrpc": "2.0",
                "error": {"code": -32600, "message": "Invalid Request"},
                "id": None
            }), 400
        
        # Validate JSON-RPC structure
        if request_data.get('jsonrpc') != '2.0':
            return jsonify({
                "jsonrpc": "2.0",
                "error": {"code": -32600, "message": "Invalid JSON-RPC version"},
                "id": request_data.get('id')
            }), 400
        
        method = request_data.get('method')
        params = request_data.get('params', {})
        req_id = request_data.get('id')
        
        logger.info(f"MCP request - Method: {method}, Params: {params}")
        
        # Handle different methods according to MCP specification
        result = None
        
        if method == 'av.function.global_quote':
            # Handle global quote request
            symbol = params.get('symbol')
            if not symbol:
                return jsonify({
                    "jsonrpc": "2.0",
                    "error": {"code": -32602, "message": "Missing symbol parameter"},
                    "id": req_id
                }), 400
            
            result = call_standard_alpha_vantage_api('GLOBAL_QUOTE', symbol=symbol)
            
        elif method == 'av.function.time_series_daily':
            # Handle time series daily request
            symbol = params.get('symbol')
            if not symbol:
                return jsonify({
                    "jsonrpc": "2.0",
                    "error": {"code": -32602, "message": "Missing symbol parameter"},
                    "id": req_id
                }), 400
            
            outputsize = params.get('outputsize', 'compact')
            result = call_standard_alpha_vantage_api('TIME_SERIES_DAILY', symbol=symbol, outputsize=outputsize)
            
        elif method == 'av.function.symbol_search':
            # Handle symbol search request
            keywords = params.get('keywords')
            if not keywords:
                return jsonify({
                    "jsonrpc": "2.0",
                    "error": {"code": -32602, "message": "Missing keywords parameter"},
                    "id": req_id
                }), 400
            
            result = call_standard_alpha_vantage_api('SYMBOL_SEARCH', keywords=keywords)
            
        elif method == 'av.function.currency_exchange_rate':
            # Handle currency exchange rate request
            from_currency = params.get('from_currency')
            to_currency = params.get('to_currency', 'USD')
            
            if not from_currency:
                return jsonify({
                    "jsonrpc": "2.0",
                    "error": {"code": -32602, "message": "Missing from_currency parameter"},
                    "id": req_id
                }), 400
            
            result = call_standard_alpha_vantage_api('CURRENCY_EXCHANGE_RATE', 
                                                    from_currency=from_currency, 
                                                    to_currency=to_currency)
                                                    
        elif method == 'av.function.crypto_overview':
            # Handle crypto overview request
            symbol = params.get('symbol')
            if not symbol:
                return jsonify({
                    "jsonrpc": "2.0",
                    "error": {"code": -32602, "message": "Missing symbol parameter"},
                    "id": req_id
                }), 400
            
            market = params.get('market', 'USD')
            result = call_standard_alpha_vantage_api('CURRENCY_EXCHANGE_RATE', 
                                                    from_currency=symbol, 
                                                    to_currency=market)
                                                    
        elif method == 'av.function.news_sentiment':
            # Handle news sentiment request
            tickers = params.get('tickers')
            topics = params.get('topics')
            time_from = params.get('time_from')
            time_to = params.get('time_to')
            sort = params.get('sort', 'LATEST')
            limit = params.get('limit', 50)
            
            # Build parameters for news sentiment API call
            news_params = {}
            if tickers:
                news_params['tickers'] = tickers
            if topics:
                news_params['topics'] = topics
            if time_from:
                news_params['time_from'] = time_from
            if time_to:
                news_params['time_to'] = time_to
            if sort:
                news_params['sort'] = sort
            if limit:
                news_params['limit'] = limit
                
            result = call_standard_alpha_vantage_api('NEWS_SENTIMENT', **news_params)
            
        else:
            # Unknown method
            return jsonify({
                "jsonrpc": "2.0",
                "error": {"code": -32601, "message": f"Method not found: {method}"},
                "id": req_id
            }), 404
        
        # Return the result according to JSON-RPC specification
        if result is not None:
            return jsonify({
                "jsonrpc": "2.0",
                "result": result,
                "id": req_id
            })
        else:
            return jsonify({
                "jsonrpc": "2.0",
                "error": {"code": -32603, "message": "Internal error calling Alpha Vantage API"},
                "id": req_id
            }), 500
    
    except Exception as e:
        logger.error(f"Error in MCP handler: {str(e)}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        
        req_id = None
        try:
            request_data = request.get_json()
            req_id = request_data.get('id') if request_data else None
        except:
            pass  # If we can't parse the request, req_id stays None
        
        return jsonify({
            "jsonrpc": "2.0",
            "error": {"code": -32603, "message": "Internal error in MCP server"},
            "id": req_id
        }), 500