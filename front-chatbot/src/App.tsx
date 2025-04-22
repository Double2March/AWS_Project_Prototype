import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import Chat from './components/chat';
import './App.css';

const Home = () => {
  const [username, setUsername] = useState('');
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    if (username.trim()) {
      setIsLoggedIn(true);
    }
  };

  return (
    <div className="home-container">
      {!isLoggedIn ? (
        <div className="login-form">
          <h2>채팅 애플리케이션</h2>
          <form onSubmit={handleLogin}>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="사용자 이름을 입력하세요"
              required
            />
            <button type="submit">입장</button>
          </form>
        </div>
      ) : (
        <Chat username={username} />
      )}
    </div>
  );
};

const SecondPage = () => {
  return (
    <div className="second-page">
      <h2>두번째 페이지</h2>
      <p>이곳은 두번째 페이지입니다.</p>
      <Link to="/">홈으로 돌아가기</Link>
    </div>
  );
};

const App: React.FC = () => {
  return (
    <Router>
      <div className="app">
        <nav className="navbar">
          <Link to="/">홈</Link>
          <Link to="/second">두번째 페이지</Link>
        </nav>
        <div className="content">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/second" element={<SecondPage />} />
          </Routes>
        </div>
      </div>
    </Router>
  );
};

export default App;