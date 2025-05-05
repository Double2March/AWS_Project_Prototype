# main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from api.chatSingle import router as chat_single_router
from api.chatStream import router as chat_stream_router
from api.chatCreateProject import router as invoke_bedrock_router

app = FastAPI()

origins = [
    "http://localhost:5173",  # React 앱의 주소
    "http://localhost",       # localhost 허용
    "http://127.0.0.1:5173"  # localhost:5173 허용 (다양한 경우 추가 가능)
]

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# router 등록
app.include_router(chat_single_router)
app.include_router(chat_stream_router)
app.include_router(invoke_bedrock_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)