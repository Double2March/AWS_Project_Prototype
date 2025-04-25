// stream 코드
const [messages, setMessages] = useState<Message[]>([]);
const [newMessage, setNewMessage] = useState('');
const [downloadUrls, setDownloadUrls] = useState<string[]>([]);
const [isLoading, setIsLoading] = useState(false);
const [currentResponse, setCurrentResponse] = useState('');
const messagesEndRef = useRef<HTMLDivElement>(null);

// const back_chat_url = import.meta.env.VITE_APP_BASE_URL+"stream";

// 스크롤을 항상 최신 메시지로 이동
const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
};

useEffect(() => {
    scrollToBottom();
}, [messages, currentResponse]);

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
    setCurrentResponse('');

    try {
    const response = await fetch(`http://3.38.255.228:8000/api/chat/stream`, {
        method: 'POST',
        headers: {
        'Content-Type': 'application/json',
        },
        body: JSON.stringify({
        prompt: userInput,
        systemPrompt: prompt_first
        }),
    });

    // 응답을 읽기 위한 reader 생성
    const reader = response.body!.getReader();
    const decoder = new TextDecoder();
    
    // 응답 스트림 처리
    while (true) {
        const { done, value } = await reader.read();
        
        if (done) {
        // 스트림이 완료되면 종료
        break;
        }
        
        // 디코딩된 텍스트
        const text = decoder.decode(value);
        
        console.log('Decoded text:', text); // 디코딩된 텍스트를 확인

        // SSE 이벤트 파싱
        const events = text.split('\n\n').filter(e => e.trim() !== '');
        
        for (const event of events) {
        if (event.startsWith('data: ')) {
            try {
            const data = JSON.parse(event.substring(6));
            if (data.done) {
                // 스트림 완료 - 메시지 배열에 AI 응답 추가
                finishResponse();
                break;
            }
            
            // 응답 텍스트 추가
            if (data.text) {
                setCurrentResponse(prev => prev + data.text);
            }

            // presigned URL 처리 (만약 서버에서 제공한다면)
            if (data.presignedUrls && data.presignedUrls.length > 0) {
                setDownloadUrls(data.presignedUrls);
            }
            } catch (error) {
            console.error('Error parsing event data:', error);
            }
        }
        }
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
    //setMessages(prevMessages => [...prevMessages, errorMessage]);
    setIsLoading(false);
    }
}
