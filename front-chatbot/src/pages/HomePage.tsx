import { Link } from 'react-router-dom';

const HomePage = () => {
  return (
    <div>
      <h1>홈페이지</h1>
      <Link to="/chat">채팅하러 가기</Link>
    </div>
  );
};

export default HomePage;