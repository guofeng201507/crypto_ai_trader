"""
Configuration for the trade chatbot
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Alpha Vantage Configuration
# Support for multiple API keys with rotation to handle rate limits
ALPHA_VANTAGE_API_KEYS = os.environ.get('ALPHA_VANTAGE_API_KEYS', '20KCRQCE82CTCDVI,8DW7GH8FIZDXGFHC').split(',')
# Clean up any extra whitespace
ALPHA_VANTAGE_API_KEYS = [key.strip() for key in ALPHA_VANTAGE_API_KEYS if key.strip()]
# Fallback single key for backward compatibility
ALPHA_VANTAGE_API_KEY = os.environ.get('ALPHA_VANTAGE_API_KEY', '20KCRQCE82CTCDVI')
ALPHA_VANTAGE_BASE_URL = 'https://www.alphavantage.co/query'

# Key rotation state (will be initialized in the key manager)
CURRENT_KEY_INDEX = 0

# Application Configuration
DEBUG = os.environ.get('DEBUG', 'True').lower() == 'true'
SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key')
CONTEXT_STORAGE_PATH = os.environ.get('CONTEXT_STORAGE_PATH', 'context_storage')

# Server Configuration
HOST = os.environ.get('HOST', '0.0.0.0')
PORT = int(os.environ.get('PORT', 5000))

# API Configuration
API_VERSION = 'v1'
MAX_MESSAGE_LENGTH = 1000
API_PREFIX = '/api'