from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from typing import Optional
import logging
from service.websocketService import manager

# 로거 설정
logger = logging.getLogger("websocket")

# 라우터 생성
router = APIRouter()

@router.websocket("/api/chat/ws")
async def websocket_endpoint(
    websocket: WebSocket, 
    tag: Optional[str] = Query(None)
):
    await manager.connect(websocket)
    
    try:
        # 환영 메시지 전송
        await websocket.send_text("백엔드 출력 모니터링에 연결되었습니다.")
        logger.info("새 웹소켓 클라이언트가 연결되었습니다.")
        
        # 무한 루프 - 클라이언트로부터 메시지를 기다림 (연결 유지)
        while True:
            data = await websocket.receive_text()
            # 메시지 수신 시 처리 (필요한 경우 확장)
            if data.startswith("/test"):
                # 테스트 메시지 명령어 처리
                count = 5  # 기본값
                if len(data.split()) > 1:
                    try:
                        count = int(data.split()[1])
                    except ValueError:
                        pass
                    
                # 테스트 출력 생성
                for i in range(count):
                    print(f"테스트 출력 #{i+1}")
                    if i % 3 == 0:
                        logger.warning(f"테스트 경고 메시지 #{i+1}")
                    if i % 5 == 0:
                        logger.error(f"테스트 오류 메시지 #{i+1}")
    
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("웹소켓 클라이언트 연결이 종료되었습니다.")
    except Exception as e:
        logger.error(f"웹소켓 오류 발생: {str(e)}")
        manager.disconnect(websocket)