# Trade Chatbot

A web-based chatbot for trading and financial data queries with context engineering, Yahoo Finance integration, and Qwen AI capabilities.

## Features

- Web-based chat interface similar to ChatGPT with left-aligned markdown rendering
- Context management to maintain conversation history
- Integration with Yahoo Finance for real-time stock, cryptocurrency, and precious metals data
- Alpha Vantage MCP server integration as a fallback data source
- Qwen AI integration for advanced natural language understanding
- Ability to interpret natural language queries and map them to appropriate financial symbols (e.g., "gold" to XAUUSD, "bitcoin" to BTC-USD)
- Support for multiple asset types including stocks, cryptocurrencies, precious metals, and forex pairs
- Responsive design for desktop and mobile
- Automatic interpretation of financial asset requests (e.g., "What's the price of gold?" or "How much is Bitcoin?")

## Tech Stack

### Backend
- Flask (Python web framework)
- Requests (for API calls)
- Pandas (for data manipulation)
- OpenAI library (to interface with Qwen API)
- python-dotenv (for environment variable management)

### Frontend
- React (UI library)
- Webpack (module bundler)
- Axios (HTTP client)
- react-markdown (for rendering markdown content)

## Setup Instructions

### Backend Setup

1. Install Python dependencies:
```bash
cd trade_chatbot
pip install -r requirements.txt
```

2. Create a `.env` file in the root of the project with your API keys (see `.env.example` for reference):
```bash
QWEN_API_KEY=your_qwen_api_key
QWEN_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
SECRET_KEY=your_secret_key_here
DEBUG=True
```

3. Start the backend server:
```bash
cd trade_chatbot/backend
python app.py
```

The backend will start on `http://localhost:5001`.

### Frontend Setup

1. Navigate to the frontend directory and install dependencies:
```bash
cd trade_chatbot/frontend
npm install
```

2. Start the development server:
```bash
npm start
```

The frontend will start on `http://localhost:3000` and will proxy API requests to the backend running on port 5001.

## API Endpoints

### Chat Endpoint
- **POST** `/api/chat`
- Request body: `{"message": "your message", "user_id": "optional_user_id"}`
- Response: `{"response": "bot response", "context": "conversation context"}`

### Stock Data Endpoint
- **GET** `/api/data/stock/{symbol}`
- Response: Stock information for the given symbol

### MCP (Model Context Protocol) Endpoints
- **GET** `/api/mcp/quote?symbol={symbol}`
  - Get quote for a given symbol from Alpha Vantage MCP server
- **GET** `/api/mcp/time_series_daily?symbol={symbol}`
  - Get daily time series data for a given symbol from Alpha Vantage MCP server
- **GET** `/api/mcp/sector`
  - Get sector performance data from Alpha Vantage MCP server

## Context Engineering

The chatbot maintains conversation context for each user to provide more relevant responses based on previous interactions. Context is stored in the `context_storage` directory by default.

## Yahoo Finance Integration

The system integrates with Yahoo Finance API to retrieve real-time and historical financial data for stocks, cryptocurrencies, precious metals, and forex pairs. The API doesn't require an API key.

## Qwen AI Integration

The system uses Qwen API through the compatible mode (OpenAI-compatible) to provide advanced natural language processing capabilities. When users ask about financial assets in natural language (e.g., "What's the price of gold?"), the AI interprets the request and maps it to the appropriate financial symbol before retrieving data from Yahoo Finance.

## Supported Assets

The chatbot supports various asset types, automatically interpreting natural language queries:

### Stocks
- Query: "What is the price of AAPL?"
- Supported: Any major stock symbol (AAPL, MSFT, TSLA, etc.)

### Cryptocurrencies
- Query: "How much is Bitcoin?" or "Price of BTC"
- Supported: BTC-USD, ETH-USD, LTC-USD, XRP-USD, etc.

### Precious Metals
- Query: "What's the price of gold?" or "Price of XAU/USD"
- Supported: XAUUSD (Gold), XAGUSD (Silver), XPTUSD (Platinum), XPDUSD (Palladium)

### Additional Assets
- Oil, Gas, Copper, and other commodities
- Forex pairs like EURUSD, JPYUSD, GBPUSD, etc.

## Configuration

The system's behavior is configurable via the `prompts.py` file in the config directory:
- `FINANCIAL_KEYWORDS`: Keywords that trigger financial asset interpretation
- `ASSET_SYMBOL_MAPPING`: Mapping of asset names to financial symbols
- Various prompt templates for different scenarios

## Usage Examples

- "What is the price of AAPL?"
- "Tell me about Tesla stock"
- "What's the current market trend?"
- "Compare Apple and Microsoft stock prices"
- "Should I buy this stock?"
- "Analyze the market sentiment"
- "What's the price of gold?"
- "How much is Bitcoin?"
- "Price of silver today"

## Development

To run in development mode with hot reloading:

1. Ensure your `.env` file is properly configured with valid API keys
2. Start the backend server
3. In a separate terminal, start the frontend development server:
```bash
cd trade_chatbot/frontend
npm start
```

## Production Deployment

For production deployment, build the frontend and serve both backend and frontend appropriately:

1. Build the frontend:
```bash
cd trade_chatbot/frontend
npm run build
```

2. Deploy the backend with the built frontend files.

3. Ensure environment variables are properly set in your production environment.

## License

This project is licensed under the MIT License.