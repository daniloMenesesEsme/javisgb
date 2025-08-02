import React, { useState } from 'react';
import './Login.css'; // Certifique-se de que este arquivo CSS existe ou crie-o

function Login({ onLogin }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  
  // URL base do backend
  const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5001';

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      const response = await fetch(`${API_BASE_URL}/api/auth`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
      });
      
      if (response.ok) {
        onLogin(username);
      } else {
        setError('Usuário ou senha inválidos.');
      }
    } catch (error) {
      // Fallback para desenvolvimento (remover em produção)
      if (username === 'admin' && password === 'boticario2024') {
        onLogin(username);
      } else {
        setError('Usuário ou senha inválidos.');
      }
    }
  };

  return (
    <div className="login-container">
      <form onSubmit={handleSubmit} className="login-form">
        <div className="logo-container">
          <img 
            className="logo" 
            src="/logo-boticario.png" 
            alt="Grupo Boticário" 
            width="80" 
            height="80"
            onError={(e) => {
              // Fallback se não encontrar o PNG
              e.target.style.display = 'none';
              e.target.nextSibling.style.display = 'block';
            }}
          />
          <div className="logo-fallback" style={{display: 'none', fontSize: '60px'}}>🏪</div>
          <h2>Grupo Boticário</h2>
        </div>
        <p style={{color: '#718096', marginBottom: '32px', fontSize: '1.1em'}}>
          Assistente Virtual para Suporte
        </p>
        {error && <p className="error-message">{error}</p>}
        <div className="form-group">
          <label htmlFor="username">Usuário:</label>
          <input
            type="text"
            id="username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
          />
        </div>
        <div className="form-group">
          <label htmlFor="password">Senha:</label>
          <input
            type="password"
            id="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </div>
        <button type="submit">Entrar</button>
      </form>
    </div>
  );
}

export default Login;
