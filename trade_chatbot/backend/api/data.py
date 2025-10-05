"""
Data API endpoints for the trade chatbot
"""
from flask import Blueprint, request, jsonify
from ..utils.helpers import get_stock_data
import logging

logger = logging.getLogger(__name__)

data_bp = Blueprint('data', __name__)

@data_bp.route('/stock/<symbol>', methods=['GET'])
def get_stock_info(symbol):
    """
    Get stock information for a given symbol
    """
    try:
        logger.info(f"Received request for stock data: {symbol}")
        stock_data = get_stock_data(symbol)
        
        if stock_data:
            logger.info(f"Returning stock data for {symbol}: {stock_data}")
            return jsonify(stock_data), 200
        else:
            logger.warning(f'No data found for symbol {symbol}')
            return jsonify({'error': f'No data found for symbol {symbol}'}), 404
    except Exception as e:
        logger.error(f"Error in get_stock_info for {symbol}: {str(e)}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500