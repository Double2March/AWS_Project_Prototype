import ReactMarkdown from 'react-markdown';
import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { v4 as uuidv4 } from 'uuid';

import rehypeRaw from 'rehype-raw';
import rehypeHighlight from 'rehype-highlight';

interface Message {
  id: string;
  text: string;
  sender: string;
  timestamp: Date;
  isAction?: boolean; // Add this property to identify clickable action messages
  actionType?: string; // To identify what type of action this is
  isButtonDisabled?: boolean; // To track if a button has already been clicked
  processingComplete?: boolean; // To track if processing is complete
}

interface ChatProps {
  username: string;
}

const Chat: React.FC<ChatProps> = ({ username }) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [newMessage, setNewMessage] = useState('');
  const [downloadUrls, setDownloadUrls] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [sessionUuid, setSessionUuid] = useState<string>(''); 
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [isCreatingProject, setIsCreatingProject] = useState(false);

  const API_URL = import.meta.env.VITE_APP_BASE_URL;
  const textareaRef = useRef<HTMLTextAreaElement>(null);

   // 컴포넌트 마운트 시 UUID 초기화
   useEffect(() => {
    // 로컬 스토리지에서 UUID 가져오기
    const savedUuid = localStorage.getItem('chatSessionUuid');
    
    if (savedUuid) {
      // 이미 저장된 UUID가 있다면 사용
      setSessionUuid(savedUuid);
    } else {
      // 없다면 새로 생성하고 저장
      const newUuid = uuidv4();
      localStorage.setItem('chatSessionUuid', newUuid);
      setSessionUuid(newUuid);
    }

    const systemMessage: Message = {
      id: Date.now().toString() + '-init',
      text: ` **======== 입력예시 =========**
**기본 정보**
○ 서비스명 (영어):
○ 서비스 목적: 
**기능 요구사항**
●
●
●
**기술 스택**
○ 프론트엔드 (선택): 
○ 백엔드 (선택): 
○ 데이터베이스 (선택): 
○ 클라우드 환경 (선택):`,
      sender: 'System',
      timestamp: new Date(),
    };
    setMessages([systemMessage]);


  }, []);

  // 스크롤을 항상 최신 메시지로 이동
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);


  const handleSendMessage = async () => {
    if (!newMessage.trim()) return;

    setDownloadUrls([]);

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

    if (textareaRef.current) {
      textareaRef.current.style.height = '40px'; // 초기 높이로 재설정
    }

   
    try {
      // 한 번에 응답받는 방식
      const response = await axios.post(`${API_URL}/single`, {
        uid: sessionUuid,
        prompt: userInput,
        timestamp: new Date().toISOString()
      });
      

      // 응답 메시지 추가
      if (response.data.answer) {
    
        const aiResponseMessage: Message = {
          id: Date.now().toString() + '-ai',
          text: response.data.answer,
          sender: 'System',
          timestamp: new Date(),
        };
        setMessages(prevMessages => [...prevMessages, aiResponseMessage]);

        if (response.data.create) {
          // 프로젝트 생성 액션 버튼 추가
        const createProjectAction: Message = {
          id: Date.now().toString() + '-action',
          text: "프로젝트 만들기",
          sender: 'System',
          timestamp: new Date(),
          isAction: true,
          actionType: 'createProject',
          isButtonDisabled: false
        };
        setMessages(prevMessages => [...prevMessages, createProjectAction]);
        }        
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

  const handleTextareaChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setNewMessage(e.target.value);
    
    // 높이 자동 조절
    e.target.style.height = 'auto';
    e.target.style.height = `${e.target.scrollHeight}px`;
  };

  // 프로젝트 생성 API 호출 함수
  const handleCreateProject = async (messageId: string) => {
    setIsLoading(true);
    setIsCreatingProject(true);

    try {
      // 버튼이 있는 메시지를 찾아 비활성화 상태로 변경
      setMessages(prevMessages => 
        prevMessages.map(msg => 
          msg.id === messageId 
            ? {...msg, isButtonDisabled: true, processingComplete: false} 
            : msg
        )
      );
      
      // 세션션저장된 UUID 사용
      const response = await axios.post(`${API_URL}/createProject`, {
        uid: sessionUuid, // 세션에 저장된 UUID 사용
        timestamp: new Date().toISOString()
      });
    
      // 응답 메시지 추가
      const responseMessage: Message = {
        id: Date.now().toString() + '-project-response',
        text: response.data.answer,
        sender: 'System',
        timestamp: new Date(),
      };

      // presigned URL 처리 (만약 서버에서 제공한다면)
      if (response.data.presignedUrls && response.data.presignedUrls.length > 0) {
        setDownloadUrls(response.data.presignedUrls);
      }
      
      // 처리가 완료되었음을 표시
      setMessages(prevMessages => {
        // 먼저 액션 버튼의 상태를 업데이트
        const updatedMessages = prevMessages.map(msg => 
          msg.id === messageId 
            ? {...msg, processingComplete: true} 
            : msg
        );
        
        // 그 다음에 새 응답 메시지 추가
        return [...updatedMessages, responseMessage];
      });
      
    } catch (error) {
      console.error('프로젝트 생성 중 오류 발생:', error);
      // 오류 메시지 표시
      const errorMessage: Message = {
        id: Date.now().toString() + '-project-error',
        text: '프로젝트 생성 중 오류가 발생했습니다.',
        sender: 'System',
        timestamp: new Date(),
      };
      
      // 오류 발생 시에도 버튼 상태를 업데이트
      setMessages(prevMessages => {
        // 먼저 액션 버튼의 상태를 업데이트
        const updatedMessages = prevMessages.map(msg => 
          msg.id === messageId 
            ? {...msg, processingComplete: true} 
            : msg
        );
        
        // 그 다음에 오류 메시지 추가
        return [...updatedMessages, errorMessage];
      });
    } finally {
      setIsLoading(false);
      setIsCreatingProject(false);
    }
  };

  // 로딩 텍스트 컴포넌트
  const LoadingText = () => {
    const [dots, setDots] = useState<string>('.');
    
    useEffect(() => {
      const interval = setInterval(() => {
        setDots(prevDots => {
          if (prevDots === '.') return '..';
          if (prevDots === '..') return '...';
          if (prevDots === '...') return '....';
          return '.';
        });
      }, 500);
      
      return () => clearInterval(interval);
    }, []);
    
    return <strong>생성중입니다{dots}</strong>;
  };



  // 메시지 렌더링 함수
  const renderMessage = (message: Message) => {
    // 액션 버튼인 경우 클릭 가능한 버튼으로 렌더링
    if (message.isAction) {
      // 처리가 완료되었고 버튼이 비활성화 상태면 아무것도 렌더링하지 않음
      if (message.isButtonDisabled && message.processingComplete) {
        return null;
      }
      
      return (
        <div 
          key={message.id} 
          className={`message ${message.sender === username ? 'own-message' : 'other-message'} action-message`}
        >
          {message.isButtonDisabled ? (
            <div className="action-button-disabled">
              <LoadingText />
            </div>
          ) : (
            <button 
              className="action-button"
              onClick={() => {
                if (message.actionType === 'createProject') {
                  handleCreateProject(message.id);
                }
              }}
              disabled={isLoading || message.isButtonDisabled}
            >
              {message.text}
            </button>
          )}
          <div className="message-time">
            {message.timestamp.toLocaleTimeString()}
          </div>
        </div>
      );
    }

    
    // 일반 메시지인 경우 기존 방식으로 렌더링
    return (
      <div 
        key={message.id} 
        className={`message ${message.sender === username ? 'own-message' : 'other-message'}`}
      >
        <div className="message-text"><ReactMarkdown 
          rehypePlugins={[rehypeRaw, rehypeHighlight]}>
          {message.text}
          </ReactMarkdown>
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
        
        {/* 로딩 중인 응답 표시 */}
        {isLoading && !isCreatingProject && (
          <div className="message other-message">
            <div className="message-text">
              답변을 생성하고 있습니다...
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
          {downloadUrls.map((url, index) => (
              <a href={url} target="_blank" rel="noopener noreferrer">
              결과 파일 {index + 1} 다운로드
            </a>
            ))}
        </div>
      )}

      <div className="message-input">
        <textarea 
          ref={textareaRef}
          value={newMessage} 
          onChange={handleTextareaChange}
          placeholder="메시지를 입력하세요..." 
          disabled={isLoading || isCreatingProject}
          onKeyDown={(e: React.KeyboardEvent<HTMLTextAreaElement>) => {
            if (e.key === 'Enter' && !e.shiftKey) {
              e.preventDefault();
              handleSendMessage();
            }
          }}
          style={{ height: 'auto' }}
        />
        <button onClick={handleSendMessage} disabled={isLoading || isCreatingProject}>
          {isLoading ? '전송 중...' : '전송'}
        </button>
      </div>

    </div>
  );
};

export default Chat;