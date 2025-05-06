import { Link } from 'react-router-dom';

const ChatPage = () => {
  return (
    <div>
      <h1>백엔드 로그</h1>
      <Link to="/log">홈으로 돌아가기</Link>
    </div>
  );
};

export default ChatPage;