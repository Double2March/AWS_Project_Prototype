import React, { useState, useEffect, useRef } from 'react';
import prompt_first from '../prompt/prompt_first';
import axios from 'axios';

interface Message {
  id: string;
  text: string;
  sender: string;
  timestamp: Date;
}

interface ChatProps {
  username: string;
}

const Chat: React.FC<ChatProps> = ({ username }) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [newMessage, setNewMessage] = useState('');
  const [downloadUrls, setDownloadUrls] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const API_URL = import.meta.env.VITE_APP_BASE_URL;
  console.log(`${API_URL}`+"/single");

  // 스크롤을 항상 최신 메시지로 이동
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async () => {
    if (!newMessage.trim()) return;

    // 새 메시지 객체 생성
    const messageObj: Message = {
      id: Date.now().toString(),
      text: newMessage,
      sender: username,
      timestamp: new Date(),
    };

    // UI에 메시지 추가
    setMessages(prevMessages => [...prevMessages, messageObj]);
    
    // 입력 필드 초기화 및 로딩 상태 설정
    const userInput = newMessage;
    setNewMessage('');
    setIsLoading(true);

    try {
      // 한 번에 응답받는 방식
      const response = await axios.post(`${API_URL}`+"/single", {
        prompt: userInput,
        systemPrompt: prompt_first
      });

      console.log('응답 데이터:', response.data);

      // 응답 메시지 추가
      if (response.data.answer) {
        const aiResponseMessage: Message = {
          id: Date.now().toString() + '-ai',
          text: response.data.answer,
          sender: 'System',
          timestamp: new Date(),
        };
        setMessages(prevMessages => [...prevMessages, aiResponseMessage]);
      }

      // presigned URL 처리 (만약 서버에서 제공한다면)
      if (response.data.presignedUrls && response.data.presignedUrls.length > 0) {
        setDownloadUrls(response.data.presignedUrls);
      }
    } catch (error) {
      console.error('메시지 전송 중 오류 발생:', error);
      // 오류 메시지 표시
      const errorMessage: Message = {
        id: Date.now().toString() + '-error',
        text: '메시지 전송 중 오류가 발생했습니다.',
        sender: 'System',
        timestamp: new Date(),
      };
      setMessages(prevMessages => [...prevMessages, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  // Enter 키 처리 함수
  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !isLoading) {
      handleSendMessage();
    }
  };

  return (
    <div className="chat-container">
      <div className="messages-container">
        {messages.map((message) => (
          <div 
            key={message.id} 
            className={`message ${message.sender === username ? 'own-message' : 'other-message'}`}
          >
            <div className="message-text">{message.text}</div>
            <div className="message-time">
              {message.timestamp.toLocaleTimeString()}
            </div>
          </div>
        ))}
        
        {/* 로딩 중인 응답 표시 */}
        {isLoading && (
          <div className="message other-message">
            <div className="message-text">
              생각 중입니다...
            </div>
            <div className="message-time">
              {new Date().toLocaleTimeString()}
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {downloadUrls.length > 0 && (
        <div className="download-links">
          <h4>다운로드 가능한 파일:</h4>
          <ul>
            {downloadUrls.map((url, index) => (
              <li key={index}>
                <a href={url} target="_blank" rel="noopener noreferrer">
                  결과 파일 {index + 1} 다운로드
                </a>
              </li>
            ))}
          </ul>
        </div>
      )}

      <div className="message-input">
        <input
          type="text"
          value={newMessage}
          onChange={(e) => setNewMessage(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="메시지를 입력하세요..."
          disabled={isLoading}
        />
        <button onClick={handleSendMessage} disabled={isLoading}>
          {isLoading ? '전송 중...' : '전송'}
        </button>
      </div>
    </div>
  );
};

export default Chat;