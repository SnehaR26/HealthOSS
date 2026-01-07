import React, { useState, useRef, useEffect } from 'react';
import './App.css';

function App() {
  const [messages, setMessages] = useState([
    { role: 'assistant', content: 'Hello! I am your Health Assistant. How can I help you today?' }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const scrollRef = useRef(null);

  // Auto-scroll to bottom of chat
  useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage = { role: 'user', content: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await fetch('http://127.0.0.1:8080/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: input }), // Matches your UserQuery model
      });

      const data = await response.json();
      setMessages((prev) => [...prev, { role: 'assistant', content: data.response }]);
    } catch (error) {
      setMessages((prev) => [...prev, { role: 'assistant', content: 'Error: Could not connect to backend.' }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="app-container">
      <header className="app-header">
        <h1>🌿 HealthOSS</h1>
        <p>Your Multi-Agent Wellness Partner</p>
      </header>

      <div className="chat-window">
        {messages.map((msg, idx) => (
          <div key={idx} className={`message-bubble ${msg.role}`}>
            <div className="message-content">{msg.content}</div>
          </div>
        ))}
        {isLoading && <div className="message-bubble assistant">Thinking...</div>}
        <div ref={scrollRef} />
      </div>

      <div className="input-area">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSend()}
          placeholder="Log spend, ask about fitness, or check sleep..."
        />
        <button onClick={handleSend} disabled={isLoading}>Send</button>
      </div>
    </div>
  );
}

export default App;