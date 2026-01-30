import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    loadHistory();
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const loadHistory = async () => {
    try {
      const response = await axios.get('http://localhost:5000/api/history');
      if (response.data.success) {
        // History loaded successfully
      }
    } catch (error) {
      console.error('Failed to load history:', error);
    }
  };

  const sendMessage = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMessage = input;
    setInput('');
    setMessages([...messages, { type: 'user', text: userMessage }]);
    setLoading(true);

    try {
      const response = await axios.post('http://localhost:5000/api/chat', { message: userMessage });
      if (response.data.success) {
        setMessages((prev) => [
          ...prev,
          { type: 'infini', text: response.data.reply }
        ]);
      }
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        { type: 'error', text: 'Error getting response. Try again.' }
      ]);
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  const clearChat = async () => {
    try {
      await axios.post('http://localhost:5000/api/clear-history');
      setMessages([]);
    } catch (error) {
      console.error('Failed to clear history:', error);
    }
  };

  return (
    <div className="app">
      <div className="container">
        <header className="header">
          <h1>🔥 Infini Think</h1>
          <p>Your sarcastic multilingual AI assistant</p>
        </header>

        <div className="chat-container">
          <div className="messages">
            {messages.length === 0 && (
              <div className="welcome">
                <h2>Welcome to Infini Think</h2>
                <p>Say something to get started!</p>
              </div>
            )}
            {messages.map((msg, index) => (
              <div key={index} className={`message ${msg.type}`}>
                <div className="message-content">
                  {msg.type === 'infini' && <span className="badge">🔥 Infini Think</span>}
                  {msg.type === 'user' && <span className="badge">You</span>}
                  {msg.type === 'error' && <span className="badge">❌ Error</span>}
                  <p>{msg.text}</p>
                </div>
              </div>
            ))}
            {loading && (
              <div className="message infini">
                <div className="message-content">
                  <span className="badge">🔥 Infini Think</span>
                  <div className="typing">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          <form onSubmit={sendMessage} className="input-form">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Type your message..."
              disabled={loading}
              autoFocus
            />
            <button type="submit" disabled={loading || !input.trim()}>
              Send
            </button>
          </form>

          <button onClick={clearChat} className="clear-btn">
            Clear Chat
          </button>
        </div>
      </div>
    </div>
  );
}

export default App;