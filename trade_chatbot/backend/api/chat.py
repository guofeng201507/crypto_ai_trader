"""
Chat API endpoints for the trade chatbot
"""
from flask import Blueprint, request, jsonify
from ..context_engine.context_manager import ContextManager
from ..utils.helpers import get_stock_data
import os
import requests
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

# Configure Qwen API
qwen_api_key = os.environ.get("QWEN_API_KEY")
qwen_base_url = os.environ.get("QWEN_BASE_URL")

chat_bp = Blueprint('chat', __name__)

# Initialize context manager
context_manager = ContextManager()

@chat_bp.route('/chat', methods=['POST'])
def chat():
    """
    Main chat endpoint that processes user queries and returns responses
    """
    try:
        data = request.get_json()
        user_message = data.get('message', '')
        user_id = data.get('user_id', 'default_user')
        
        logger.info(f"Received chat request: user_id={user_id}, message='{user_message}'")
        
        if not user_message:
            error_msg = 'Message is required'
            logger.error(error_msg)
            return jsonify({'error': error_msg}), 400
        
        # Validate Qwen API credentials
        if not qwen_api_key or not qwen_base_url:
            error_msg = "Qwen API key or base URL not configured"
            logger.error(error_msg)
            return jsonify({'error': error_msg}), 500
        
        # Retrieve context for the user
        try:
            context = context_manager.get_context(user_id)
            logger.info(f"Retrieved context with {len(context)} previous interactions")
        except Exception as context_error:
            logger.error(f"Error retrieving context: {str(context_error)}")
            context = []
        
        # Generate response based on user message and context using Qwen API
        try:
            response = generate_response_with_qwen(user_message, context)
            logger.info(f"Generated response: '{response}'")
        except Exception as gen_error:
            logger.error(f"Error generating response: {str(gen_error)}")
            response = "I encountered an issue processing your request. Please try again later."
        
        # Update context with the new interaction
        try:
            context_manager.update_context(user_id, user_message, response)
        except Exception as update_error:
            logger.error(f"Error updating context: {str(update_error)}")
        
        # Ensure response is a string
        if not isinstance(response, str):
            response = str(response)
        
        response_json = {
            'response': response,
            'context': context if context else []
        }
        
        logger.info("Sending response back to client")
        
        return jsonify(response_json), 200
    except Exception as e:
        error_msg = f"Server error: {str(e)}"
        logger.error(error_msg)
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        return jsonify({'error': error_msg}), 500

def generate_response_with_qwen(user_message, context):
    """
    Generate a response using the Qwen API with the provided user message and context.
    """
    try:
        # Check if the message is about stock or crypto data
        user_message_lower = user_message.lower()
        if any(word in user_message_lower for word in ['stock', 'price', 'symbol', 'ticker', 'bitcoin', 'ethereum', 'crypto', 'btc', 'eth']):
            # Extract potential symbol from message
            import re
            symbols = re.findall(r'\b([A-Z]{3,5}|BTC|ETH|LTC|BCH|BNB|EOS|XRP|XLM|ADA|TRX|USDT|DOT|UNI)\b', user_message)
            
            if symbols:
                symbol = symbols[0].upper()  # Take the first symbol found and convert to uppercase
                data = get_stock_data(symbol)  # This now handles both stocks and crypto
                
                if data:
                    # Determine if it's stock or cryptocurrency data for appropriate formatting
                    is_crypto = 'market' in data  # Cryptocurrency data has 'market' field
                    
                    if is_crypto:
                        # Format cryptocurrency data
                        crypto_info = f" cryptocurrency: {data.get('symbol')}/{data.get('market')}\n" \
                                    f"Current Price: {data.get('price', 'N/A')} {data.get('market')}\n" \
                                    f"Bid Price: {data.get('open', 'N/A')} {data.get('market')}\n" \
                                    f"Ask Price: {data.get('high', 'N/A')} {data.get('market')}\n" \
                                    f"Last Refreshed: {data.get('last_refreshed', 'N/A')}\n" \
                                    f"Summary: {data.get('summary', 'N/A')}"
                        
                        # Create a detailed prompt for the Qwen API
                        prompt = f"Based on the following cryptocurrency data:\n{crypto_info}\n\n" \
                                 f"Answer the user's query: '{user_message}'\n\n" \
                                 f"Provide a comprehensive and helpful response about this cryptocurrency."
                    else:
                        # Format stock data
                        stock_info = f"Stock: {data.get('symbol')}\n" \
                                    f"Current Price: ${data.get('price', 'N/A')}\n" \
                                    f"Today's High: ${data.get('high', 'N/A')}\n" \
                                    f"Today's Low: ${data.get('low', 'N/A')}\n" \
                                    f"Change: {data.get('change', 'N/A')} ({data.get('change_percent', 'N/A')})\n" \
                                    f"Volume: {data.get('volume', 'N/A')}\n" \
                                    f"Previous Close: ${data.get('previous_close', 'N/A')}\n" \
                                    f"Summary: {data.get('summary', 'N/A')}"
                        
                        # Create a detailed prompt for the Qwen API
                        prompt = f"Based on the following stock data:\n{stock_info}\n\n" \
                                 f"Answer the user's query: '{user_message}'\n\n" \
                                 f"Provide a comprehensive and helpful response about this stock."
                else:
                    prompt = f"The user asked about the symbol '{symbol}', which could be a stock or cryptocurrency, but I couldn't retrieve the data. " \
                             f"Please inform the user that the symbol might be incorrect or unavailable, " \
                             f"and suggest they check the symbol and try again. Respond to their query: '{user_message}'"
            else:
                prompt = f"The user's query is: '{user_message}'. " \
                         f"It seems to be related to financial assets, but no specific symbol was provided. " \
                         f"Please ask the user to specify a symbol (e.g., AAPL, BTC, ETH) for more accurate information."
        else:
            # For non-stock/cryptocurrency related queries, create a context-aware prompt
            context_str = "\n".join([f"User: {item['user_message']}\nBot: {item['bot_response']}" 
                                     for item in context[-5:]])  # Use last 5 exchanges as context
            
            prompt = f"Context from previous conversation:\n{context_str}\n\n" \
                     f"Current user query: '{user_message}'\n\n" \
                     f"Please provide a helpful response related to trading, finance, or markets. " \
                     f"If the query is not related to trading or finance, politely redirect to those topics."
        
        logger.info(f"Qwen API request prompt: {prompt}")
        
        # Prepare headers and payload for the API request
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {qwen_api_key}"
        }
        
        payload = {
            "model": "qwen-max",  # You can change this to other available models
            "messages": [
                {"role": "system", "content": "You are a knowledgeable trading and finance assistant. Provide accurate, helpful, and concise responses related to trading, finance, stocks, and markets. Use the provided context and data to inform your responses. Be professional and helpful."},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 500,
            "temperature": 0.7
        }
        
        logger.info(f"Making request to: {qwen_base_url}/chat/completions")
        
        # Make a request to the Qwen API using requests library
        response = requests.post(
            f"{qwen_base_url}/chat/completions",
            headers=headers,
            json=payload,
            timeout=30  # Adding a timeout to avoid hanging requests
        )
        
        logger.info(f"Qwen API response status: {response.status_code}")
        logger.info(f"Qwen API response: {response.text}")
        
        # Raise an exception for bad status codes
        response.raise_for_status()
        
        # Parse the response
        response_data = response.json()
        
        if 'choices' in response_data and len(response_data['choices']) > 0:
            content = response_data['choices'][0]['message']['content']
            logger.info(f"Qwen API response content: {content}")
            return content
        else:
            logger.error(f"No choices in Qwen API response: {response_data}")
            return "I received a response from the AI service, but couldn't extract the answer. Please try again."
        
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP error calling Qwen API: {str(e)}")
        logger.error(f"Response content: {response.text}")
        return f"I encountered an HTTP error while processing your request: {str(e)}. " \
               "Please try again later."
    except requests.exceptions.RequestException as e:
        # Handle network-related errors
        logger.error(f"Network error calling Qwen API: {str(e)}")
        return f"I encountered a network issue processing your request: {str(e)}. " \
               "Please try again later or ask about stock prices with a specific symbol."
    except KeyError as e:
        # Handle case where expected keys are missing from response
        logger.error(f"Key error calling Qwen API: {str(e)}")
        logger.error(f"Response data: {response_data if 'response_data' in locals() else 'response_data not defined'}")
        return "I received a response from the AI service, but couldn't extract the answer. Please try again."
    except Exception as e:
        # Fallback to rule-based response if the API call fails
        logger.error(f"Unexpected error calling Qwen API: {str(e)}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        return f"I encountered an issue processing your request: {str(e)}. " \
               "Please try again later or ask about stock prices with a specific symbol."