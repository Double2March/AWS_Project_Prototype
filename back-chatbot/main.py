from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import logging

# 기존 라우터
from api.chatSingle import router as chat_single_router
from api.chatStream import router as chat_stream_router
from api.chatCreateProject import router as invoke_bedrock_router

# 웹소켓 라우터 및 서비스 추가
from api.websocket import router as websocket_router
# 기존 import 변경
from service.websocketService import manager, send_to_websocket, ws_logger  # setup_print_redirect 대신 새 함수들 임포트

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger("main")

app = FastAPI()

origins = [
    "http://localhost:5173",  # React 앱의 주소
    "http://localhost",       # localhost 허용
    "http://127.0.0.1:5173"   # localhost:5173 허용 (다양한 경우 추가 가능)
]

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 기존 라우터 등록
app.include_router(chat_single_router)
app.include_router(chat_stream_router)
app.include_router(invoke_bedrock_router)

# 웹소켓 라우터 등록
app.include_router(websocket_router)

# 애플리케이션 시작 시 이벤트
@app.on_event("startup")
async def startup_event():
    # 기존 setup_print_redirect() 호출 제거
    logger.info("서버가 시작되었습니다.")
    # 웹소켓으로 메시지 전송
    send_to_websocket("서버가 시작되었습니다.", "INFO")

# 애플리케이션 종료 시 이벤트
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("서버가 종료됩니다.")
    send_to_websocket("서버가 종료됩니다.", "INFO")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)