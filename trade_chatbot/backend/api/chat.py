"""Chat API endpoints for the trade chatbot."""
from flask import Blueprint, request, jsonify
from pathlib import Path
from ..context_engine.context_manager import ContextManager
from ..utils.helpers import get_stock_data
from ..config.prompts import FINANCIAL_KEYWORDS, INTERPRETATION_PROMPT_TEMPLATE, ASSET_INFO_PROMPT_TEMPLATE, STOCK_INFO_PROMPT_TEMPLATE, FALLBACK_PROMPT_TEMPLATE, NO_SYMBOL_PROMPT_TEMPLATE, GENERAL_CHAT_PROMPT_TEMPLATE
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

# Load environment variables from root .env
project_root = Path(__file__).resolve().parent.parent.parent.parent
load_dotenv(project_root / ".env")

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
        # Check if the message is about financial assets using configurable keywords
        user_message_lower = user_message.lower()
        is_financial_query = any(keyword in user_message_lower for keyword in FINANCIAL_KEYWORDS)
        
        if is_financial_query:
            # First, ask the LLM to interpret the user's request and provide the appropriate symbol
            interpretation_prompt = INTERPRETATION_PROMPT_TEMPLATE.format(user_message=user_message)

            # Prepare headers and payload for the interpretation API request
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {qwen_api_key}"
            }

            interpretation_payload = {
                "model": "qwen-max",
                "messages": [
                    {"role": "system", "content": "You are a financial symbol interpreter. You only return the appropriate financial symbol for the given query. No explanations, no additional text."},
                    {"role": "user", "content": interpretation_prompt}
                ],
                "max_tokens": 100,
                "temperature": 0.3
            }

            # Make a request to the Qwen API to interpret the symbol
            interpretation_response = requests.post(
                f"{qwen_base_url}/chat/completions",
                headers=headers,
                json=interpretation_payload,
                timeout=30
            )

            interpretation_response.raise_for_status()
            interpretation_data = interpretation_response.json()

            if 'choices' in interpretation_data and len(interpretation_data['choices']) > 0:
                interpreted_symbol = interpretation_data['choices'][0]['message']['content'].strip()
                
                # Now fetch the actual data for the interpreted symbol
                data = get_stock_data(interpreted_symbol)
                
                if data:
                    # Format the data appropriately based on type
                    if '-USD' in interpreted_symbol or interpreted_symbol in ['XAUUSD', 'XAGUSD', 'XPTUSD', 'XPDUSD']:
                        # Format cryptocurrency or precious metals data
                        asset_info = f"Asset: {data.get('symbol')}\n" \
                                    f"Current Price: {data.get('price', 'N/A')}\n" \
                                    f"Today's High: {data.get('high', 'N/A')}\n" \
                                    f"Today's Low: {data.get('low', 'N/A')}\n" \
                                    f"Change: {data.get('change', 'N/A')} ({data.get('change_percent', 'N/A')})\n" \
                                    f"Volume: {data.get('volume', 'N/A')}\n" \
                                    f"Previous Close: {data.get('previous_close', 'N/A')}\n" \
                                    f"Summary: {data.get('summary', 'N/A')}"
                        
                        # Use the configured prompt template
                        prompt = ASSET_INFO_PROMPT_TEMPLATE.format(
                            asset_type="asset",
                            asset_info=asset_info,
                            user_message=user_message
                        )
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
                        
                        # Use the configured prompt template
                        prompt = STOCK_INFO_PROMPT_TEMPLATE.format(
                            stock_info=stock_info,
                            user_message=user_message
                        )
                else:
                    # Use the fallback prompt template
                    prompt = FALLBACK_PROMPT_TEMPLATE.format(
                        user_message=user_message,
                        interpreted_symbol=interpreted_symbol
                    )
            else:
                # Use the no-symbol prompt template
                prompt = NO_SYMBOL_PROMPT_TEMPLATE.format(user_message=user_message)
        else:
            # For non-stock/cryptocurrency related queries, create a context-aware prompt
            context_str = "\n".join([f"User: {item['user_message']}\nBot: {item['bot_response']}" 
                                     for item in context[-5:]])  # Use last 5 exchanges as context
            
            # Use the general chat prompt template
            prompt = GENERAL_CHAT_PROMPT_TEMPLATE.format(
                context_str=context_str,
                user_message=user_message
            )
        
        logger.info(f"Qwen API request prompt: {prompt}")
        
        # Prepare headers and payload for the main API request
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {qwen_api_key}"
        }
        
        payload = {
            "model": "qwen-max",  # You can change this to other available models
            "messages": [
                {"role": "system", "content": "You are a knowledgeable trading and finance assistant. Provide accurate, helpful, and concise responses related to trading, finance, stocks, and markets. Use the provided context and data to inform your responses. Be professional and helpful. Keep all responses under 150 words for brevity."},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 200,  # Reduced token limit to enforce 150-word constraint
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