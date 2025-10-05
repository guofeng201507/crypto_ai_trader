import React, { useState, useEffect } from 'react';
import ChatInterface from './components/ChatInterface';
import './App.css';

function App() {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  // Load any existing conversation from localStorage on component mount
  useEffect(() => {
    const savedMessages = localStorage.getItem('tradeChatMessages');
    if (savedMessages) {
      setMessages(JSON.parse(savedMessages));
    }
  }, []);

  // Save messages to localStorage whenever they change
  useEffect(() => {
    localStorage.setItem('tradeChatMessages', JSON.stringify(messages));
  }, [messages]);

  return (
    <div className="App">
      <header className="app-header">
        <h1>Trade Chatbot</h1>
        <p>Ask me about stock prices, market data, and trading insights</p>
      </header>
      <main>
        <ChatInterface 
          messages={messages} 
          setMessages={setMessages} 
          isLoading={isLoading}
          setIsLoading={setIsLoading}
        />
      </main>
    </div>
  );
}

export default App;