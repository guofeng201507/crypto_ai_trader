"""
Trade Chatbot - Backend Application

This module sets up a Flask-based API for a trading chatbot
with context engineering and Alpha Vantage integration.
"""

from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
import os
import sys
from pathlib import Path
import logging

# Set up logging to capture all errors
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Add the project root directory to the Python path to allow absolute imports
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

# Load environment variables from .env file
load_dotenv()

def create_app():
    app = Flask(__name__)
    
    # Enable CORS for cross-origin requests
    CORS(app)
    
    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
    app.config['ALPHA_VANTAGE_API_KEY'] = os.environ.get(
        'ALPHA_VANTAGE_API_KEY', 
        '20KCRQCE82CTCDVI'  # Default key from MCP server
    )
    
    # Register blueprints - use absolute imports to avoid relative import issues
    from trade_chatbot.backend.api.chat import chat_bp
    from trade_chatbot.backend.api.data import data_bp
    from trade_chatbot.backend.api.mcp import mcp_bp
    from trade_chatbot.backend.api.mcp_wrapper import mcp_wrapper_bp
    
    app.register_blueprint(chat_bp, url_prefix='/api')
    app.register_blueprint(data_bp, url_prefix='/api')
    app.register_blueprint(mcp_bp, url_prefix='/api/mcp')
    app.register_blueprint(mcp_wrapper_bp, url_prefix='/api/mcp_wrapper')  # This will be our new MCP-compatible endpoint
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5001)