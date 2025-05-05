import ReactMarkdown from 'react-markdown';
import React, { useState, useEffect, useRef } from 'react';
import { v4 as uuidv4 } from 'uuid';

interface Message {
  id: string;
  text: string;
  sender: string;
  timestamp: Date;
}

interface LogChatProps {
  username: string;
  wsUrl: string;
}

const LogChat: React.FC<LogChatProps> = ({ username, wsUrl }) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isConnected, setIsConnected] = useState<boolean>(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const webSocketRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    // 이미 연결된 소켓이 있는지 확인
    if (webSocketRef.current && 
       (webSocketRef.current.readyState === WebSocket.CONNECTING || 
        webSocketRef.current.readyState === WebSocket.OPEN)) {
      console.log('이미 연결된 WebSocket이 있습니다. 새 연결을 생성하지 않습니다.');
      return;
    }
  
    console.log('새 WebSocket 연결을 생성합니다.');
    const connectWebSocket = () => {
      // 기존 코드...
    };
  
    connectWebSocket();
    
    return () => {
      if (webSocketRef.current) {
        webSocketRef.current.close();
      }
    };
  }, [wsUrl]);
  
  // 컴포넌트 마운트 시 웹소켓 연결
  useEffect(() => {

    // 웹소켓 연결 생성
    const connectWebSocket = () => {
      try {
        const ws = new WebSocket(wsUrl);
        
        ws.onopen = () => {
          console.log('WebSocket 연결 성공');
          setIsConnected(true);
          
          // 연결 성공 메시지 추가
          const connectMessage: Message = {
            id: uuidv4(),
            text: '백엔드 서버에 연결되었습니다. 출력값을 수신합니다...',
            sender: 'System',
            timestamp: new Date(),
          };
          setMessages(prev => [...prev, connectMessage]);
        };
        
        ws.onmessage = (event) => {
          // 서버로부터 메시지 수신
          const logMessage: Message = {
            id: uuidv4(),
            text: event.data,
            sender: 'Backend',
            timestamp: new Date(),
          };
          setMessages(prev => [...prev, logMessage]);
        };
        
        ws.onerror = (error) => {
          console.error('WebSocket 오류:', error);
          setIsConnected(false);
          
          // 오류 메시지 추가
          const errorMessage: Message = {
            id: uuidv4(),
            text: 'WebSocket 연결 중 오류가 발생했습니다.',
            sender: 'System',
            timestamp: new Date(),
          };
          setMessages(prev => [...prev, errorMessage]);
        };
        
        ws.onclose = () => {
          console.log('WebSocket 연결 종료');
          setIsConnected(false);
          
          // 연결 종료 메시지 추가
          const closeMessage: Message = {
            id: uuidv4(),
            text: '백엔드 서버와의 연결이 종료되었습니다. 재연결 시도 중...',
            sender: 'System',
            timestamp: new Date(),
          };
          setMessages(prev => [...prev, closeMessage]);
          
          // 3초 후 재연결 시도
          setTimeout(connectWebSocket, 3000);
        };
        
        webSocketRef.current = ws;
      } catch (error) {
        console.error('WebSocket 연결 실패:', error);
        setTimeout(connectWebSocket, 3000);
      }
    };

    connectWebSocket();
    
    // 컴포넌트 언마운트 시 웹소켓 연결 종료
    return () => {
      if (webSocketRef.current) {
        webSocketRef.current.close();
      }
    };
  }, [wsUrl]);

  // 스크롤을 항상 최신 메시지로 이동
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // 테스트 로그 생성 요청
  const handleGenerateTestLogs = () => {
    if (webSocketRef.current && webSocketRef.current.readyState === WebSocket.OPEN) {
      webSocketRef.current.send("/test");
      
      // 테스트 요청 메시지 추가
      const testRequestMessage: Message = {
        id: uuidv4(),
        text: '테스트 로그 생성 요청을 보냈습니다.',
        sender: username,
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, testRequestMessage]);
    } else {
      // 연결 없음 메시지 추가
      const noConnectionMessage: Message = {
        id: uuidv4(),
        text: '서버에 연결되어 있지 않습니다.',
        sender: 'System',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, noConnectionMessage]);
    }
  };

  // 로그 지우기
  const handleClearLogs = () => {
    setMessages([]);
  };

  // 메시지 렌더링 함수
  const renderMessage = (message: Message) => {
    // 서버 로그 메시지 특별 스타일링
    const isBackendLog = message.sender === 'Backend';
    
    return (
      <div 
        key={message.id} 
        className={`message ${message.sender === username ? 'own-message' : 'other-message'} ${isBackendLog ? 'backend-log' : ''}`}
      >
        <div className="message-text">
          <ReactMarkdown>{message.text}</ReactMarkdown>
        </div>
        <div className="message-time">
          {message.timestamp.toLocaleTimeString()}
        </div>
      </div>
    );
  };

  return (
    <div className="chat-container">
      <div className="messages-container">
        {messages.map(renderMessage)}
        <div ref={messagesEndRef} />
      </div>

      <div className="message-input">
        <div className="connection-status">
          {isConnected ? (
            <span className="status-connected">연결됨</span>
          ) : (
            <span className="status-disconnected">연결 끊김</span>
          )}
        </div>
        
        <button 
          className="clear-logs-button" 
          onClick={handleClearLogs}
        >
          로그 지우기
        </button>
        
        <button 
          className="test-logs-button" 
          onClick={handleGenerateTestLogs}
          disabled={!isConnected}
        >
          테스트 로그 생성
        </button>
      </div>
    </div>
  );
};

export default LogChat;