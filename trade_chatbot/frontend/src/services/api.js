import axios from 'axios';

// Create an axios instance with more robust configuration
const apiClient = axios.create({
  baseURL: '/api', // This will be proxied to the backend by webpack dev server
  timeout: 30000, // 30 seconds timeout (increased for AI processing)
  headers: {
    'Content-Type': 'application/json',
  }
});

// Request interceptor to log requests
apiClient.interceptors.request.use(
  config => {
    console.log('API Request:', config.method?.toUpperCase(), config.url, config.data);
    return config;
  },
  error => {
    console.error('Request error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor to log responses and handle errors
apiClient.interceptors.response.use(
  response => {
    console.log('API Response:', response.status, response.data);
    return response;
  },
  error => {
    console.error('Response error:', error.response?.status, error.response?.data || error.message);
    return Promise.reject(error);
  }
);

// Function to send a message to the chatbot
export const sendMessage = async (message) => {
  try {
    console.log('Sending message to chatbot:', message);
    const response = await apiClient.post('/chat', {
      message: message,
      user_id: 'default_user' // In a real app, you would use the actual user ID
    });
    
    // Validate the response structure
    if (!response.data || typeof response.data.response !== 'string') {
      throw new Error('Invalid response format from server');
    }
    
    return response.data;
  } catch (error) {
    console.error('Error sending message:', error);
    
    // Provide more specific error messages based on error type
    if (error.response) {
      // Server responded with error status
      if (error.response.status >= 500) {
        throw new Error('Server error: The service is temporarily unavailable. Please try again later.');
      } else if (error.response.status === 400) {
        throw new Error('Bad request: Please check your input and try again.');
      } else {
        throw new Error(`Request failed: ${error.response.data.error || 'Unknown error'}`);
      }
    } else if (error.request) {
      // Request was made but no response received
      throw new Error('Network error: Unable to reach the server. Please check your connection.');
    } else {
      // Other errors
      throw new Error(`Error: ${error.message}`);
    }
  }
};

// Function to get stock data
export const getStockData = async (symbol) => {
  try {
    console.log(`Requesting stock data for: ${symbol}`);
    const response = await apiClient.get(`/data/stock/${symbol}`);
    
    return response.data;
  } catch (error) {
    console.error(`Error getting stock data for ${symbol}:`, error);
    
    if (error.response) {
      if (error.response.status >= 500) {
        throw new Error('Server error: Unable to retrieve stock data. Please try again later.');
      } else if (error.response.status === 404) {
        throw new Error(`No data found for symbol: ${symbol}`);
      } else {
        throw new Error(`Request failed: ${error.response.data.error || 'Unknown error'}`);
      }
    } else if (error.request) {
      throw new Error('Network error: Unable to reach the server.');
    } else {
      throw new Error(`Error: ${error.message}`);
    }
  }
};