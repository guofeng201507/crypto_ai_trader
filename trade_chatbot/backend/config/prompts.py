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

# Asset information prompt template - More friendly and conversation-like
ASSET_INFO_PROMPT_TEMPLATE = """Hey there! Based on the latest market data I pulled for you:

{asset_info}

Regarding your question: '{user_message}'

Here's what I can tell you about this {asset_type} - I've kept it concise (under 150 words) so you can quickly get the info you need!"""

# Stock information prompt template - More friendly and conversation-like
STOCK_INFO_PROMPT_TEMPLATE = """Hey there! I've got the latest stock data for you:

{stock_info}

Regarding your question: '{user_message}'

Here's my take on this stock - quick and to the point (under 150 words)!"""

# Fallback prompt when no data is found - More friendly and conversation-like
FALLBACK_PROMPT_TEMPLATE = """Hmm, I had a look at '{user_message}' which I thought was about the symbol '{interpreted_symbol}', but I couldn't pull up any data. 
This could mean the symbol is a bit off or maybe not available right now. 

Could you double-check the symbol and give it another shot? For example, try AAPL for Apple or BTC for Bitcoin.

What would you like to try instead?"""

# Prompt for when no specific symbol is provided - More friendly and conversation-like
NO_SYMBOL_PROMPT_TEMPLATE = """I see you're asking about financial assets with: '{user_message}'. 
To give you the most accurate info, could you be a bit more specific? 

For example:
- For stocks: AAPL (Apple), MSFT (Microsoft), TSLA (Tesla)
- For crypto: BTC (Bitcoin), ETH (Ethereum)
- For metals: XAUUSD (Gold), XAGUSD (Silver)

What exactly would you like to know about?"""

# General chat prompt template - More friendly and conversation-like
GENERAL_CHAT_PROMPT_TEMPLATE = """Here's what we've talked about recently:
{context_str}

Now you're asking: '{user_message}'

As your trading assistant, I'll keep this under 150 words so it's easy to digest. 
Let me give you a quick, helpful response about trading, finance, or markets!

If your question isn't related to those areas, I'll gently steer you back to topics I can really help with."""