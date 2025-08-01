import React, { useState, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import './Chat.css';

function Chat({ username }) {
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [isConnected, setIsConnected] = useState(false);
  const [isLoading, setIsLoading] = useState(false); // Estado para controlar o carregamento

  useEffect(() => {
    // Verifica a conexão com o backend ao montar o componente
    const checkConnection = async () => {
      try {
        const response = await fetch('http://localhost:5001/'); // Rota básica para verificar o status
        if (response.ok) {
          setIsConnected(true);
        } else {
          setIsConnected(false);
        }
      } catch (error) {
        setIsConnected(false);
      }
    };

    checkConnection();
    const interval = setInterval(checkConnection, 5000); // Verifica a cada 5 segundos
    return () => clearInterval(interval);
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!newMessage) return;

    const userMessage = { text: newMessage, sender: 'user' };
    setMessages(prevMessages => [...prevMessages, userMessage]);
    setNewMessage('');
    setIsLoading(true); // Ativa o indicador de carregamento

    try {
      const response = await fetch(`${apiUrl}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: newMessage }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      const botMessage = { text: data.response, sender: 'bot' };
      setMessages(prevMessages => [...prevMessages, botMessage]);

    } catch (error) {
      console.error('Error sending message:', error);
      const errorBotMessage = { text: "Erro: Não foi possível obter uma resposta do bot. Verifique se o servidor está online.", sender: 'bot' };
      setMessages(prevMessages => [...prevMessages, errorBotMessage]);

    } finally {
      setIsLoading(false); // Desativa o indicador de carregamento
    }
  };

  return (
    <div className="chat-container">
      <div className="connection-status">
        {isConnected ? <strong>{`Seja Bem vindo ${username}! Em que posso ajudar hoje!`}</strong> : 'Desconectado'}
      </div>
      <div className="message-list">
        {messages.map((message, index) => (
          <div key={index} className={`message ${message.sender}`}>
            {message.sender === 'bot' ? (
              <ReactMarkdown>{message.text}</ReactMarkdown>
            ) : (
              message.text
            )}
          </div>
        ))}
        {isLoading && (
          <div className="message bot">
            <p><i>Analisando os documentos e preparando sua resposta...</i></p>
          </div>
        )}
      </div>
      <form onSubmit={handleSubmit} className="input-form">
        <input
          type="text"
          value={newMessage}
          onChange={(e) => setNewMessage(e.target.value)}
          placeholder="Digite sua mensagem..."
        />
        <button type="submit">Enviar</button>
      </form>
    </div>
  );
}

export default Chat;