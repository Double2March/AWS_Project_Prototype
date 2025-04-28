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

# AWS 클라이언트 초기화
lambda_client = boto3.client('lambda', region_name='ap-northeast-2')
s3_client = boto3.client('s3', region_name='ap-northeast-2')

# S3 버킷 이름
BUCKET_NAME = "your-s3-bucket-name"  # 실제 S3 버킷 이름으로 변경하세요


@app.post("/chat", response_model=ChatResponse)
async def process_chat(chat_message: ChatMessage):
    try:
        # 메시지 ID 생성
        message_id = str(uuid.uuid4())
        """
        # 첫 번째 람다 함수 호출
        first_lambda_response = invoke_lambda("first-lambda-function", {
            "message": chat_message.message,
            "username": chat_message.username,
            "timestamp": chat_message.timestamp,
            "message_id": message_id
        })
        """
        first_lambda_result = "첫번재 람다 결과"
        
        """
        first_lambda_result = first_lambda_response.get("result", "첫 번째 람다 함수 응답이 없습니다.")
        
        # 두 번째, 세 번째 람다 함수를 비동기적으로 호출
        second_lambda_task = asyncio.create_task(invoke_lambda_async("second-lambda-function", {
            "message": chat_message.message,
            "username": chat_message.username,
            "timestamp": chat_message.timestamp,
            "message_id": message_id,
            "first_lambda_result": first_lambda_result
        }))
        
        third_lambda_task = asyncio.create_task(invoke_lambda_async("third-lambda-function", {
            "message": chat_message.message,
            "username": chat_message.username,
            "timestamp": chat_message.timestamp,
            "message_id": message_id,
            "first_lambda_result": first_lambda_result
        }))
        
        # 람다 함수 결과 동시에 기다림
        second_lambda_response, third_lambda_response = await asyncio.gather(
            second_lambda_task,
            third_lambda_task
        )
        """
        # 람다 결과 처리
        second_lambda_result = "두번째 람다 결과"
        third_lambda_result = "세번째 람다 결과"
        
        """
        second_lambda_result = second_lambda_response.get("result", "두 번째 람다 함수 응답이 없습니다.")
        third_lambda_result = third_lambda_response.get("result", "세 번째 람다 함수 응답이 없습니다.")
        
        # 결과 파일 생성 및 S3에 업로드
        presigned_urls = ["presigned urls"]
        
        
        # 두 번째 람다 결과 파일 생성 및 업로드
        second_lambda_file = f"second_lambda_result_{message_id}.txt"
        upload_to_s3(second_lambda_file, process_lambda_result(second_lambda_result))
        presigned_urls.append(generate_presigned_url(second_lambda_file))
        
        # 세 번째 람다 결과 파일 생성 및 업로드
        third_lambda_file = f"third_lambda_result_{message_id}.txt"
        upload_to_s3(third_lambda_file, process_lambda_result(third_lambda_result))
        presigned_urls.append(generate_presigned_url(third_lambda_file))
        """
        
        presigned_urls = ["링크주소 입니다","두번째요"]
        
        return ChatResponse(
            firstLambdaResult=first_lambda_result,
            presignedUrls=presigned_urls
        )
        
    except Exception as e:
        traceback.print_exc()  # 전체 에러 스택 출력
        raise HTTPException(status_code=500, detail=f"처리 중 오류 발생: {str(e)}")

def invoke_lambda(function_name, payload):
    """람다 함수를 동기적으로 호출"""
    response = lambda_client.invoke(
        FunctionName=function_name,
        InvocationType='RequestResponse',
        Payload=json.dumps(payload)
    )
    
    return json.loads(response['Payload'].read().decode('utf-8'))

async def invoke_lambda_async(function_name, payload):
    """람다 함수를 비동기적으로 호출"""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None, 
        lambda: invoke_lambda(function_name, payload)
    )

def process_lambda_result(result):
    """람다 함수 결과 처리"""
    # 여기서 람다 결과를 가공할 수 있습니다
    processed_result = f"처리 시간: {datetime.now().isoformat()}\n\n{result}"
    return processed_result

def upload_to_s3(file_name, content):
    """S3에 파일 업로드"""
    s3_client.put_object(
        Bucket=BUCKET_NAME,
        Key=file_name,
        Body=content.encode('utf-8')
    )

def generate_presigned_url(file_name):
    """S3 파일에 대한 presigned URL 생성"""
    return s3_client.generate_presigned_url(
        'get_object',
        Params={
            'Bucket': BUCKET_NAME,
            'Key': file_name
        },
        ExpiresIn=3600  # URL 유효 기간: 1시간
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)