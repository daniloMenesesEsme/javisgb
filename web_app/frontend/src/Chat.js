import React, { useState, useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import './Chat.css';

function Chat({ username }) {
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [isConnected, setIsConnected] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const messageListRef = useRef(null);
  
  // URL base do backend - adaptável para diferentes ambientes
  const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5001';

  // Auto-scroll to bottom of message list
  useEffect(() => {
    if (messageListRef.current) {
      messageListRef.current.scrollTop = messageListRef.current.scrollHeight;
    }
  }, [messages]);

  // Check backend connection status
  useEffect(() => {
    const checkConnection = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/`);
        setIsConnected(response.ok);
      } catch (error) {
        setIsConnected(false);
      }
    };
    checkConnection();
    const interval = setInterval(checkConnection, 5000);
    return () => clearInterval(interval);
  }, []);

  const handleFeedback = async (messageId, feedbackType) => {
    const messageIndex = messages.findIndex(msg => msg.id === messageId);
    if (messageIndex === -1) return;

    const message = messages[messageIndex];
    const userQuestion = messages[messageIndex - 1]?.text || "Contexto não encontrado";

    try {
      await fetch(`${API_BASE_URL}/feedback`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          question: userQuestion,
          answer: message.text,
          feedback: feedbackType,
        }),
      });

      // Update message state to reflect that feedback was given
      setMessages(prev =>
        prev.map(msg =>
          msg.id === messageId ? { ...msg, feedback: feedbackType } : msg
        )
      );
    } catch (error) {
      console.error('Failed to send feedback:', error);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!newMessage.trim() || isLoading) return;

    const userMessage = { id: Date.now(), text: newMessage, sender: 'user' };
    const botMessagePlaceholder = { id: Date.now() + 1, text: '', sender: 'bot', sources: [], feedback: null };

    setMessages(prev => [...prev, userMessage, botMessagePlaceholder]);
    setNewMessage('');
    setIsLoading(true);

    const eventSource = new EventSource(`${API_BASE_URL}/chat?message=${encodeURIComponent(newMessage)}`);

    eventSource.onmessage = function(event) {
      const data = JSON.parse(event.data);

      setMessages(prev => {
        const lastMsgIndex = prev.length - 1;
        const updatedMessages = [...prev];
        const currentBotMessage = updatedMessages[lastMsgIndex];

        if (data.error) {
          currentBotMessage.text = `Erro: ${data.error}`;
          eventSource.close();
          setIsLoading(false);
        } else {
          if (data.sources) currentBotMessage.sources = data.sources;
          if (data.token) {
            currentBotMessage.text += data.token;
            // Se a resposta parece estar completa, feche a conexão
            if (data.token.includes('---') || data.token.endsWith('\n\n')) {
              setTimeout(() => {
                eventSource.close();
                setIsLoading(false);
              }, 1000);
            }
          }
        }
        return updatedMessages;
      });
    };

    eventSource.onerror = function(err) {
      console.error("EventSource failed:", err);
      setMessages(prev => {
          const lastMsg = prev[prev.length - 1];
          if (!lastMsg.text || lastMsg.text === '') {
            lastMsg.text = "Erro de conexão com o servidor de streaming.";
          }
          return [...prev.slice(0, -1), lastMsg];
      });
      eventSource.close();
      setIsLoading(false);
    };

    // Timeout para fechar a conexão após resposta completa
    setTimeout(() => {
      if (eventSource.readyState !== EventSource.CLOSED) {
        eventSource.close();
        setIsLoading(false);
      }
    }, 30000); // 30 segundos timeout
  };

  return (
    <div className="chat-container">
      <div className="connection-status">
        {isConnected ? (
          <div>
            <div style={{fontSize: '1.1em', fontWeight: 'bold', display: 'flex', alignItems: 'center', gap: '10px'}}>
              <img 
                src="/logo-boticario.png" 
                alt="Grupo Boticário" 
                width="24" 
                height="24" 
                style={{borderRadius: '4px'}}
                onError={(e) => {
                  // Fallback se não encontrar o PNG
                  e.target.outerHTML = '<span style="font-size: 24px;">🏪</span>';
                }}
              />
              Assistente Virtual Grupo Boticário
            </div>
            <div style={{fontSize: '0.9em', marginTop: '4px', opacity: 0.9}}>
              Olá {username}! Como posso ajudar você hoje?
            </div>
          </div>
        ) : (
          <div style={{color: '#e74c3c'}}>
            ❌ Desconectado - Verificando conexão...
          </div>
        )}
      </div>
      <div className="message-list" ref={messageListRef}>
        {messages.map((message) => (
          <div key={message.id} className={`message ${message.sender}`}>
            <div className="message-content">
              <ReactMarkdown>{message.text || (message.sender === 'bot' && "...")}</ReactMarkdown>
            </div>
            {message.sender === 'bot' && message.sources && message.sources.length > 0 && (
              <div className="message-sources">
                <strong>Fontes Consultadas:</strong>
                <ul>
                  {message.sources.map((source, i) => (
                    <li key={i}>{source.title} (<em>{source.source_file}</em>)</li>
                  ))}
                </ul>
              </div>
            )}
            {message.sender === 'bot' && !isLoading && message.text && (
              <div className="feedback-buttons">
                <button onClick={() => handleFeedback(message.id, 'positive')} disabled={message.feedback !== null} className={message.feedback === 'positive' ? 'selected' : ''}>👍</button>
                <button onClick={() => handleFeedback(message.id, 'negative')} disabled={message.feedback !== null} className={message.feedback === 'negative' ? 'selected' : ''}>👎</button>
              </div>
            )}
          </div>
        ))}
      </div>
      <form onSubmit={handleSubmit} className="input-form">
        <input
          type="text"
          value={newMessage}
          onChange={(e) => setNewMessage(e.target.value)}
          placeholder="Digite sua mensagem..."
          disabled={isLoading}
        />
        <button type="submit" disabled={isLoading}>Enviar</button>
      </form>
    </div>
  );
}

export default Chat;
