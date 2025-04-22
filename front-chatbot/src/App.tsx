import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import './App.css';
import { useNavigate } from "react-router-dom";
import { useLocation } from 'react-router-dom';
import Chat from './components/chat';


const Home = () => {
  
  const navigate = useNavigate();

  return (
    <div className="home-container">
      <div className="service-name">AWS IDEA<br/>Maker </div>
      <button type="button" onClick={() => navigate("/second")}>시작하기</button>
    </div>
  );
};

const ChatPage = () => {
  return (
    <div className="second-page">
      <Chat username="Guest"/>
    </div>
  );
};

const Navbar = () => {
  const location = useLocation();
  const isHome = location.pathname === '/';

  return (
    <nav className="navbar">
      {isHome ? (
        <Link to="/second">대화하기</Link>
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
            <Route path="/second" element={<ChatPage />} />
          </Routes>
        </div>
      </div>
    </Router>
  );
};

export default App;