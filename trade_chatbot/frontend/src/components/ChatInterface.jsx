import React, { useState, useRef, useEffect } from 'react';
import Message from './Message';
import Input from './Input';
import { sendMessage } from '../services/api';
import './ChatInterface.css';

const ChatInterface = ({ messages, setMessages, isLoading, setIsLoading }) => {
  const messagesEndRef = useRef(null);

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSendMessage = async (text) => {
    if (!text.trim()) return;

    // Add user message to the chat
    const userMessage = {
      id: Date.now(),
      text,
      sender: 'user',
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    try {
      // Send message to backend
      const response = await sendMessage(text);
      
      // Add bot response to the chat
      const botMessage = {
        id: Date.now() + 1,
        text: response.response,
        sender: 'bot',
        timestamp: new Date().toISOString(),
        context: response.context || null
      };

      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      
      // Add more informative error message based on error type
      let errorMessageText = '';
      if (error.message.includes('Network error')) {
        errorMessageText = 'Network connection issue. Please check your internet connection and try again.';
      } else if (error.message.includes('Server error')) {
        errorMessageText = 'Service temporarily unavailable. Our servers might be busy. Please try again in a few moments.';
      } else {
        errorMessageText = error.message || 'Sorry, I encountered an error processing your request. Please try again.';
      }

      const errorMessage = {
        id: Date.now() + 1,
        text: errorMessageText,
        sender: 'bot',
        timestamp: new Date().toISOString()
      };

      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="chat-interface">
      <div className="messages-container">
        {messages.length === 0 ? (
          <div className="welcome-message">
            <h3>Hello! I'm your trade assistant.</h3>
            <p>You can ask me about:</p>
            <ul>
              <li>Stock prices (e.g., "What is the price of AAPL?")</li>
              <li>Cryptocurrency prices (e.g., "What is the price of Bitcoin?")</li>
              <li>Market data and trends</li>
              <li>Trading insights</li>
            </ul>
          </div>
        ) : (
          messages.map(message => (
            <Message key={message.id} message={message} />
          ))
        )}
        {isLoading && (
          <div className="message bot-message">
            <div className="message-content">
              <div className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>
      <Input onSendMessage={handleSendMessage} isLoading={isLoading} />
    </div>
  );
};

export default ChatInterface;