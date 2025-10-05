import React, { useState } from 'react';
import './Input.css';

const Input = ({ onSendMessage, isLoading }) => {
  const [inputText, setInputText] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (inputText.trim() && !isLoading) {
      onSendMessage(inputText);
      setInputText('');
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      if (!isLoading) {
        handleSubmit(e);
      }
    }
  };

  return (
    <form className="input-form" onSubmit={handleSubmit}>
      <textarea
        className="input-textarea"
        value={inputText}
        onChange={(e) => setInputText(e.target.value)}
        onKeyPress={handleKeyPress}
        placeholder="Ask about stocks, prices, or trading..."
        disabled={isLoading}
        rows="1"
      />
      <button 
        type="submit" 
        className="send-button" 
        disabled={!inputText.trim() || isLoading}
      >
        {isLoading ? 'Sending...' : 'Send'}
      </button>
    </form>
  );
};

export default Input;