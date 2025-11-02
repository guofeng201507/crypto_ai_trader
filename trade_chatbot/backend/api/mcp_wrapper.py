"""
MCP (Model Context Protocol) server wrapper for Alpha Vantage API
This module provides an MCP-compatible interface that wraps the standard Alpha Vantage API
"""
import requests
import os
from flask import Blueprint, request, jsonify
from dotenv import load_dotenv
import logging
import json

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

# Configure Alpha Vantage API
ALPHA_VANTAGE_API_KEY = os.environ.get('ALPHA_VANTAGE_API_KEY', '20KCRQCE82CTCDVI')
ALPHA_VANTAGE_BASE_URL = 'https://www.alphavantage.co/query'

# Create the MCP wrapper blueprint
mcp_wrapper_bp = Blueprint('mcp_wrapper', __name__)

def call_standard_alpha_vantage_api(function, **params):
    """
    Call the standard Alpha Vantage API with the given function and parameters
    """
    api_params = {
        'function': function,
        'apikey': ALPHA_VANTAGE_API_KEY,
        **params
    }
    
    try:
        response = requests.get(ALPHA_VANTAGE_BASE_URL, params=api_params)
        
        if response.status_code == 200:
            try:
                data = response.json()
                return data
            except ValueError:
                logger.error(f"Response from Alpha Vantage is not valid JSON: {response.text}")
                return None
        else:
            logger.error(f"Error from Alpha Vantage API: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        logger.error(f"Exception calling Alpha Vantage API: {str(e)}")
        return None

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