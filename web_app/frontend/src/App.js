import React, { useState } from 'react';
import Login from './Login';
import Chat from './Chat';
import './Chat.css'; // Importando o CSS principal aqui

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [username, setUsername] = useState('');

  const handleLogin = (user) => {
    setIsLoggedIn(true);
    setUsername(user);
  };

  return (
    <div className="App">
      {!isLoggedIn ? (
        <Login onLogin={handleLogin} />
      ) : (
        <Chat username={username} />
      )}
    </div>
  );
}

export default App;