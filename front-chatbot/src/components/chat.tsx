import React, { useState, useEffect, useRef } from 'react';
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
  const messagesEndRef = useRef<HTMLDivElement>(null);

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
    setNewMessage('');
    console.log(messageObj);

    try {
      // 백엔드로 메시지 전송
      const response = await axios.post('http://3.88.117.24:8000/chat', {
        message: newMessage,
        username,
        timestamp: new Date().toISOString(),
      });
      console.log('메세지 전송완료');
      /*
      // 첫번째 람다 결과 처리
      if (response.data.firstLambdaResult) {
        const serverResponse: Message = {
          id: Date.now().toString() + '-server',
          text: response.data.firstLambdaResult,
          sender: 'System',
          timestamp: new Date(),
        };
        setMessages(prevMessages => [...prevMessages, serverResponse]);
      }

      // presigned URL 처리
      if (response.data.presignedUrls && response.data.presignedUrls.length > 0) {
        setDownloadUrls(response.data.presignedUrls);
      }
      */
      //console.log(response);
      //setMessages(prevMessages => [...prevMessages, messageObj]);
      
      const errorMessage: Message = {
        id: Date.now().toString() + '-error',
        text: '아래는 링크 주소 입니다.',
        sender: 'System',
        timestamp: new Date(),
      };
      setMessages(prevMessages => [...prevMessages, errorMessage]);
      
      
      
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
          onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
          placeholder="메시지를 입력하세요..."
        />
        <button onClick={handleSendMessage}>전송</button>
      </div>
    </div>
  );
};

export default Chat;