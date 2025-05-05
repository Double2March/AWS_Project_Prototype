import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import './App.css';
import { useNavigate } from "react-router-dom";
import { useLocation } from 'react-router-dom';

import Chat from './components/chat';
import LogChat from './components/LogChat'; 


const Home = () => {
  
  const navigate = useNavigate();
  
  const openLogInNewWindow = () => {
    window.open("/log", "_blank", "noopener,noreferrer");
  };

  return (
    <div className="home-container">
      <div className="service-name">AWS IDEA<br/>Maker </div>
      <button type="button" className="start-button" onClick={() => navigate("/chat")}>시작하기</button>
      <button type="button" className="backlog-button"onClick={openLogInNewWindow}>백엔드 로그 보기</button>
    </div>
  );
};

const ChatPage = () => {
  return (
    <div className="chat-page">
      <Chat username="Guest" />
    </div>
  );
};

const LogChatPage = () => {
  const WEBSOCKET_URL = import.meta.env.VITE_APP_BASE_URL;
  const wsUrl = WEBSOCKET_URL + '/ws'
  return (
    <div className="chat-page">
      <LogChat username="Guest" wsUrl={wsUrl} />
    </div>
  );
};

const Navbar = () => {
  const location = useLocation();
  const isHome = location.pathname === '/';

  return (
    <nav className="navbar">
      {isHome ? (
        <Link to="/chat">대화하기</Link>
      ) : (
        <Link to="/">돌아가기</Link>
      )}
    </nav>
  );
};

const App: React.FC = () => {
  return (
    <Router>
      <div className="app">
        <Navbar />
        <div className="content">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/chat" element={<ChatPage />} />
            <Route path="/log" element={<LogChatPage />} />
          </Routes>
        </div>
      </div>
    </Router>
  );
};

export default App;