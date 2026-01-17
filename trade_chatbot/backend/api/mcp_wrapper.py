"""MCP (Model Context Protocol) server wrapper for financial data APIs.

This module provides an MCP-compatible interface that wraps financial data APIs.
Currently uses Yahoo Finance as the primary data source.
"""
import requests
import os
from pathlib import Path
from flask import Blueprint, request, jsonify
from dotenv import load_dotenv
import logging
import json
import time
from typing import Optional, Dict
from datetime import datetime

# Load environment variables from root .env
project_root = Path(__file__).resolve().parent.parent.parent.parent
load_dotenv(project_root / ".env")

logger = logging.getLogger(__name__)

# Configure Yahoo Finance API
YAHOO_FINANCE_BASE_URL = 'https://query1.finance.yahoo.com/v8/finance/chart/'

# Create the MCP wrapper blueprint
mcp_wrapper_bp = Blueprint('mcp_wrapper', __name__)

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
        
        if response.status_code == 200:
            try:
                data = response.json()
                logger.info(f"Yahoo Finance API response: {data}")
                
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
                                "summary": f"Price: ${latest_price:.2f} "
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
            except ValueError:
                # Handle case where response is not JSON
                logger.error(f"Yahoo Finance response is not valid JSON for symbol {symbol}: {response.text}")
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
    if "-" in symbol and ("USD" in symbol or "BTC" in symbol or "ETH" in symbol or "EUR" in symbol or "GBP" in symbol):
        # Already in the correct format (e.g., BTC-USD)
        yahoo_symbol = symbol
    else:
        # Need to format it (e.g., BTC to BTC-USD)
        yahoo_symbol = f"{symbol}-{market}"
    
    return get_yahoo_finance_data(yahoo_symbol)

@mcp_wrapper_bp.route('/', methods=['POST'])
def mcp_handler():
    """
    MCP server endpoint that handles JSON-RPC requests for financial data
    Currently only supports Yahoo Finance as the data source
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
            # Handle global quote request using Yahoo Finance
            symbol = params.get('symbol')
            if not symbol:
                return jsonify({
                    "jsonrpc": "2.0",
                    "error": {"code": -32602, "message": "Missing symbol parameter"},
                    "id": req_id
                }), 400
            
            result = get_yahoo_finance_data(symbol)
            
        elif method == 'av.function.time_series_daily':
            # Handle time series daily request using Yahoo Finance
            symbol = params.get('symbol')
            if not symbol:
                return jsonify({
                    "jsonrpc": "2.0",
                    "error": {"code": -32602, "message": "Missing symbol parameter"},
                    "id": req_id
                }), 400
            
            outputsize = params.get('outputsize', 'compact')
            result = get_yahoo_finance_data(symbol)  # Simplified for now
            
        elif method == 'av.function.symbol_search':
            # Handle symbol search request - not implemented for Yahoo Finance
            keywords = params.get('keywords')
            if not keywords:
                return jsonify({
                    "jsonrpc": "2.0",
                    "error": {"code": -32602, "message": "Missing keywords parameter"},
                    "id": req_id
                }), 400
            
            # For now, return a simple response indicating this is not implemented
            result = {
                "Information": "Symbol search not implemented for Yahoo Finance in this MCP wrapper",
                "Keywords": keywords
            }
            
        elif method == 'av.function.currency_exchange_rate':
            # Handle currency exchange rate request using Yahoo Finance
            from_currency = params.get('from_currency')
            to_currency = params.get('to_currency', 'USD')
            
            if not from_currency:
                return jsonify({
                    "jsonrpc": "2.0",
                    "error": {"code": -32602, "message": "Missing from_currency parameter"},
                    "id": req_id
                }), 400
            
            # Format the currency pair for Yahoo Finance (e.g., EURUSD=X)
            if to_currency == 'USD':
                yahoo_symbol = f"{from_currency}{to_currency}=X"
            else:
                yahoo_symbol = f"{from_currency}{to_currency}=X"
            
            result = get_yahoo_finance_data(yahoo_symbol)
            
        elif method == 'av.function.crypto_overview':
            # Handle crypto overview request using Yahoo Finance
            symbol = params.get('symbol')
            if not symbol:
                return jsonify({
                    "jsonrpc": "2.0",
                    "error": {"code": -32602, "message": "Missing symbol parameter"},
                    "id": req_id
                }), 400
            
            market = params.get('market', 'USD')
            # Format the crypto symbol for Yahoo Finance (e.g., BTC-USD)
            yahoo_symbol = f"{symbol}-{market}"
            result = get_yahoo_finance_data(yahoo_symbol)
            
        elif method == 'av.function.news_sentiment':
            # Handle news sentiment request - not implemented for Yahoo Finance
            tickers = params.get('tickers')
            topics = params.get('topics')
            
            # For now, return a simple response indicating this is not implemented
            result = {
                "Information": "News sentiment not implemented for Yahoo Finance in this MCP wrapper",
                "Tickers": tickers,
                "Topics": topics
            }
            
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
                "error": {"code": -32603, "message": "Internal error calling financial data API"},
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