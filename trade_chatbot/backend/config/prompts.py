"""
Configuration file for chatbot prompts and keyword detection
"""
# Keywords that indicate a financial asset query
FINANCIAL_KEYWORDS = [
    'stock', 'price', 'symbol', 'ticker', 'bitcoin', 'ethereum', 'crypto', 
    'btc', 'eth', 'gold', 'silver', 'xau', 'xag', 'oil', 'gas', 'nvidia', 
    'nflx', 'meta', 'goog', 'msft', 'tsla', 'aapl', 'coin', 'currency',
    'forex', 'fx', 'commodity', 'etf', 'fund', 'bond', 'treasury'
]

# Mapping of asset names to their Yahoo Finance symbols
ASSET_SYMBOL_MAPPING = {
    'gold': 'XAUUSD=X',
    'silver': 'XAGUSD',
    'bitcoin': 'BTC-USD',
    'ethereum': 'ETH-USD',
    'oil': 'CLUSD',  # Crude oil
    'gas': 'NGUSD',  # Natural gas
    'copper': 'HGUSD',  # Copper
    'platinum': 'XPTUSD',
    'palladium': 'XPDUSD',
    'bitcoin cash': 'BCH-USD',
    'cardano': 'ADA-USD',
    'ripple': 'XRP-USD',
    'litecoin': 'LTC-USD',
    'binance coin': 'BNB-USD',
    'solana': 'SOL-USD',
    'dogecoin': 'DOGE-USD',
    'polkadot': 'DOT-USD',
    'uniswap': 'UNI-USD',
    'us dollar index': 'DX-Y.NYB',  # US Dollar Index
    'euro': 'EURUSD',  # EUR/USD
    'japanese yen': 'JPYUSD',  # JPY/USD
    'british pound': 'GBPUSD',  # GBP/USD
    'swiss franc': 'CHFUSD',  # CHF/USD
    'chinese yuan': 'CNYUSD',  # CNY/USD
    'canadian dollar': 'CADUSD',  # CAD/USD
    'australian dollar': 'AUDUSD',  # AUD/USD
    'mexican peso': 'MXNUSD',  # MXN/USD
    'indian rupee': 'INRUSD',  # INR/USD
}

# Default interpretation prompt template
INTERPRETATION_PROMPT_TEMPLATE = """Interpret the following user request to identify the financial asset symbol: '{user_message}'. 
Return ONLY the appropriate symbol that can be used with financial APIs (e.g., AAPL for Apple, 
BTC-USD for Bitcoin, XAUUSD for gold price in USD, etc.). 

Follow these rules:
- If the user is asking about gold, return 'XAU/USD' 
- If the user is asking about silver, return 'XAGUSD'
- If the user is asking about Bitcoin, return 'BTC-USD'
- If the user is asking about Ethereum, return 'ETH-USD'
- If the user is asking about Bitcoin Cash, return 'BCH-USD'
- If the user is asking about Cardano, return 'ADA-USD'
- If the user is asking about Ripple, return 'XRP-USD'
- If the user is asking about Litecoin, return 'LTC-USD'
- If the user is asking about Binance Coin, return 'BNB-USD'
- If the user is asking about Solana, return 'SOL-USD'
- If the user is asking about Dogecoin, return 'DOGE-USD'
- If the user is asking about Polkadot, return 'DOT-USD'
- If the user is asking about Uniswap, return 'UNI-USD'
- If the user is asking about crude oil, return 'CLUSD'
- If the user is asking about natural gas, return 'NGUSD'
- If the user is asking about copper, return 'HGUSD'
- If the user is asking about platinum, return 'XPTUSD'
- If the user is asking about palladium, return 'XPDUSD'
- If the user is asking about US Dollar Index, return 'DX-Y.NYB'
- For currency pairs, follow the format EURUSD, JPYUSD, GBPUSD, etc.
- For stocks, return the ticker symbol as is (e.g., AAPL, MSFT, TSLA)
- Just return the symbol and nothing else.
"""

# Asset information prompt template
ASSET_INFO_PROMPT_TEMPLATE = """Based on the following {asset_type} data:
{asset_info}

Answer the user's query: '{user_message}'

Provide a comprehensive and helpful response about this {asset_type}."""

# Stock information prompt template
STOCK_INFO_PROMPT_TEMPLATE = """Based on the following stock data:
{stock_info}

Answer the user's query: '{user_message}'

Provide a comprehensive and helpful response about this stock."""

# Fallback prompt when no data is found
FALLBACK_PROMPT_TEMPLATE = """The user asked about '{user_message}', which I interpreted as the symbol '{interpreted_symbol}', but I couldn't retrieve the data. 
Please inform the user that the symbol might be incorrect or unavailable, 
and suggest they check the symbol and try again. Respond to their query: '{user_message}'"""

# Prompt for when no specific symbol is provided
NO_SYMBOL_PROMPT_TEMPLATE = """The user's query is: '{user_message}'. 
It seems to be related to financial assets, but I couldn't interpret the specific symbol. 
Please ask the user to specify a symbol (e.g., AAPL, BTC, XAUUSD) for more accurate information."""

# General chat prompt template
GENERAL_CHAT_PROMPT_TEMPLATE = """Context from previous conversation:
{context_str}

Current user query: '{user_message}'

Please provide a helpful response related to trading, finance, or markets. 
If the query is not related to trading or finance, politely redirect to those topics."""