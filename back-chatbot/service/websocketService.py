import asyncio
import sys
import logging
from typing import List, Optional
from fastapi import WebSocket

# 웹소켓 연결 관리자
class WebSocketManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"[WebSocket] 클라이언트 연결됨. 현재 연결 수: {len(self.active_connections)}")
        
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        print(f"[WebSocket] 클라이언트 연결 해제됨. 현재 연결 수: {len(self.active_connections)}")
        
    async def broadcast(self, message: str, tag: str = None):
        # 태그가 있으면 메시지에 추가
        if tag:
            message = f"[{tag}] {message}"
            
        # 연결된 모든 클라이언트에 메시지 전송
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                print(f"[WebSocket] 메시지 전송 오류: {e}")
                disconnected.append(connection)
        
        # 연결이 끊긴 클라이언트 제거
        for conn in disconnected:
            if conn in self.active_connections:
                self.active_connections.remove(conn)

# 전역 웹소켓 매니저 인스턴스
manager = WebSocketManager()

# 사용자 정의 함수: 웹소켓으로 메시지 전송
def send_to_websocket(message: str, tag: str = None):
    if manager.active_connections:
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                asyncio.create_task(manager.broadcast(message, tag))
            else:
                # 이벤트 루프가 없는 경우 새 루프에서 실행
                asyncio.run(manager.broadcast(message, tag))
        except Exception as e:
            sys.stderr.write(f"[WebSocket] 메시지 브로드캐스트 오류: {str(e)}\n")

# 사용자 정의 로거 생성 (필요한 경우)
class WebSocketLogger:
    def info(self, message: str):
        print(message)  # 콘솔에 출력
        send_to_websocket(message, "INFO")
        
    def warning(self, message: str):
        print(f"Warning: {message}")  # 콘솔에 출력
        send_to_websocket(message, "WARNING")
        
    def error(self, message: str):
        print(f"Error: {message}", file=sys.stderr)  # 콘솔에 에러 출력
        send_to_websocket(message, "ERROR")
        
    def debug(self, message: str):
        print(f"Debug: {message}")  # 콘솔에 출력
        send_to_websocket(message, "DEBUG")

# 사용자가 직접 사용할 로거 인스턴스 생성
ws_logger = WebSocketLogger()