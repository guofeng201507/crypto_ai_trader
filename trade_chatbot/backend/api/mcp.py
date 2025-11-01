"""
MCP API endpoints for the trade chatbot
This module provides endpoints for interacting with the Alpha Vantage MCP server
"""
import requests
import os
import json
from flask import Blueprint, request, jsonify
from dotenv import load_dotenv
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

mcp_bp = Blueprint('mcp', __name__)

def call_mcp_server(method, params):
    """
    Make a JSON-RPC call to the Alpha Vantage MCP server
    """
    api_key = os.environ.get('ALPHA_VANTAGE_API_KEY', '20KCRQCE82CTCDVI')
    mcp_url = 'https://mcp.alphavantage.co/mcp'
    
    # Prepare the JSON-RPC request
    payload = {
        "jsonrpc": "2.0",
        "method": method,
        "params": params,
        "id": 1
    }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    try:
        logger.info(f"Making JSON-RPC request to: {mcp_url}")
        logger.info(f"Method: {method}, Params: {params}")
        
        response = requests.post(
            mcp_url,
            data=json.dumps(payload),
            headers=headers,
            timeout=30
        )
        
        logger.info(f"MCP server response status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                logger.info(f"MCP server response: {json.dumps(data, indent=2)}")
                
                if "result" in data:
                    return data["result"]
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
        logger.error(f"Unexpected error calling MCP server: {str(e)}")
        return None

@mcp_bp.route('/quote', methods=['GET'])
def get_quote():
    """
    Get a quote for a given symbol using the MCP server
    """
    symbol = request.args.get('symbol')
    
    if not symbol:
        return jsonify({'error': 'Symbol parameter is required'}), 400
    
    try:
        # Call the MCP server to get the quote
        result = call_mcp_server("alpha_vantage.global_quote", {"symbol": symbol})
        
        if result:
            return jsonify(result), 200
        else:
            return jsonify({'error': f'Failed to get quote for symbol {symbol}'}), 500
    except Exception as e:
        logger.error(f"Error in get_quote: {str(e)}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500

@mcp_bp.route('/time_series_daily', methods=['GET'])
def get_time_series_daily():
    """
    Get daily time series data for a given symbol using the MCP server
    """
    symbol = request.args.get('symbol')
    
    if not symbol:
        return jsonify({'error': 'Symbol parameter is required'}), 400
    
    try:
        # Call the MCP server to get the daily time series
        result = call_mcp_server("alpha_vantage.time_series_daily", {
            "symbol": symbol,
            "outputsize": "compact"  # or "full"
        })
        
        if result:
            return jsonify(result), 200
        else:
            return jsonify({'error': f'Failed to get time series for symbol {symbol}'}), 500
    except Exception as e:
        logger.error(f"Error in get_time_series_daily: {str(e)}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500

@mcp_bp.route('/sector', methods=['GET'])
def get_sector():
    """
    Get sector performance data using the MCP server
    """
    try:
        # Call the MCP server to get sector performance data
        result = call_mcp_server("alpha_vantage.sector", {})
        
        if result:
            return jsonify(result), 200
        else:
            return jsonify({'error': 'Failed to get sector performance data'}), 500
    except Exception as e:
        logger.error(f"Error in get_sector: {str(e)}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500