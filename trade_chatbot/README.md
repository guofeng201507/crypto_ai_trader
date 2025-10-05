# Trade Chatbot

A web-based chatbot for trading and financial data queries with context engineering, Alpha Vantage integration, and Qwen AI capabilities.

## Features

- Web-based chat interface similar to ChatGPT
- Context management to maintain conversation history
- Integration with Alpha Vantage for real-time stock data
- Qwen AI integration for advanced natural language understanding
- Ability to answer specific questions about stock prices and market data
- Responsive design for desktop and mobile

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

## Setup Instructions

### Backend Setup

1. Install Python dependencies:
```bash
cd trade_chatbot
pip install -r requirements.txt
```

2. Create a `.env` file in the root of the project with your API keys (see `.env.example` for reference):
```bash
ALPHA_VANTAGE_API_KEY=your_actual_alpha_vantage_api_key
QWEN_API_KEY=your_qwen_api_key
QWEN_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
SECRET_KEY=your_secret_key_here
DEBUG=True
```

3. Start the backend server:
```bash
cd backend
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

## Context Engineering

The chatbot maintains conversation context for each user to provide more relevant responses based on previous interactions. Context is stored in the `context_storage` directory by default.

## Alpha Vantage Integration

The system integrates with Alpha Vantage API via their MCP server to retrieve real-time and historical stock data. The API key is loaded from environment variables in the `.env` file.

## Qwen AI Integration

The system uses Qwen API through the compatible mode (OpenAI-compatible) to provide advanced natural language processing capabilities. The API key and base URL are loaded from environment variables in the `.env` file.

## Usage Examples

- "What is the price of AAPL?"
- "Tell me about Tesla stock"
- "What's the current market trend?"
- "Compare Apple and Microsoft stock prices"
- "Should I buy this stock?"
- "Analyze the market sentiment"

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