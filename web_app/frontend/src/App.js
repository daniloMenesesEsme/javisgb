import React, { useState } from 'react';
import Login from './Login';
import Chat from './Chat';
import './App.css';

function App() {
  const [username, setUsername] = useState(null);

  const handleLogin = (user) => {
    setUsername(user);
  };

  return (
    <div className="App">
      {username ? (
        <Chat username={username} />
      ) : (
        <Login onLogin={handleLogin} />
      )}
    </div>
  );
}

export default App;