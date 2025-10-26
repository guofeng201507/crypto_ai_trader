import React from 'react';
import ReactMarkdown from 'react-markdown';
import './Message.css';

const Message = ({ message }) => {
  const isUser = message.sender === 'user';
  
  // Format timestamp
  const formatTime = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <div className={`message ${isUser ? 'user-message' : 'bot-message'}`}>
      <div className="message-content">
        {isUser ? (
          // For user messages, render as plain text with line breaks
          message.text.split('\n').map((line, i) => (
            <React.Fragment key={i}>
              {line}
              {i < message.text.split('\n').length - 1 && <br />}
            </React.Fragment>
          ))
        ) : (
          // For bot messages, render as markdown
          <ReactMarkdown>{message.text}</ReactMarkdown>
        )}
      </div>
      <div className="message-timestamp">
        {formatTime(message.timestamp)}
      </div>
    </div>
  );
};

export default Message;