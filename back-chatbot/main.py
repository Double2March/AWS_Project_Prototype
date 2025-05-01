# main.py
import os
import json
import uuid
import asyncio
import boto3
import traceback

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from api.chatSingle import router as chat_single_router
from api.chatStream import router as chat_stream_router

from BaseModel import ChatMessage, ChatRequest, ChatResponse

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


@app.post("/test", response_model=ChatResponse)
async def process_chat(chat_message: ChatMessage):
    try:
        # 메시지 ID 생성
        message_id = str(uuid.uuid4())

        first_lambda_result = "첫번재 람다 결과"
    
        # 람다 결과 처리
        second_lambda_result = "두번째 람다 결과"
        third_lambda_result = "세번째 람다 결과"
    
        presigned_urls = ["링크주소 입니다","두번째요"]
        
        return ChatResponse(
            firstLambdaResult=first_lambda_result,
            presignedUrls=presigned_urls
        )
        
        
    except Exception as e:
        traceback.print_exc()  # 전체 에러 스택 출력
        raise HTTPException(status_code=500, detail=f"처리 중 오류 발생: {str(e)}")

@app.post("/chat", response_model=ChatResponse)
async def process_chat(chat_message: ChatRequest):

    try:
        # 메시지 ID 생성
        message_id = str(uuid.uuid4())
        
        first_lambda_result = "첫번재 람다 결과"
        
        # 람다 결과 처리
        second_lambda_result = "두번째 람다 결과"
        third_lambda_result = "세번째 람다 결과"
        
        presigned_urls = ["링크주소 입니다","두번째요"]
        
        return ChatResponse(
            firstLambdaResult=first_lambda_result,
            presignedUrls=presigned_urls
        )
        
    except Exception as e:
        traceback.print_exc()  # 전체 에러 스택 출력
        raise HTTPException(status_code=500, detail=f"처리 중 오류 발생: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)