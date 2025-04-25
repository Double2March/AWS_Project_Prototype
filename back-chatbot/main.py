# main.py
import os
import re
import json
import uuid
import asyncio
import boto3
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from BaseModel import ChatMessage, ChatRequest, ChatResponse

import traceback

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

# AWS 클라이언트 초기화
lambda_client = boto3.client('lambda', region_name='ap-northeast-2')
s3_client = boto3.client('s3', region_name='ap-northeast-2')

# S3 버킷 이름
BUCKET_NAME = "your-s3-bucket-name"  # 실제 S3 버킷 이름으로 변경하세요

async def generate_bedrock_stream(prompt: str, system_prompt: str):
    # Bedrock 클라이언트 초기화
    bedrock_runtime = boto3.client(
        service_name='bedrock-runtime',
        region_name='ap-northeast-2'  # 사용 중인 리전
    )
    
    # 페이로드 구성
    payload = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 3000,
        "temperature": 0.2,
        "top_p": 0.2,
        "top_k": 50,
        "system": system_prompt,
        "messages": [
            {
                "role": "user", 
                "content": prompt
            }
        ]
    }
    
    # 스트리밍 응답 호출
    response = bedrock_runtime.invoke_model_with_response_stream(
        modelId='anthropic.claude-3-5-sonnet-20240620-v1:0',
        contentType="application/json",
        accept= "application/json",
        body=json.dumps(payload)
    )
    
    # 스트림 처리
    for event in response.get('body'):
        if 'chunk' in event:
            chunk_data = json.loads(event['chunk']['bytes'])
            print(chunk_data)
            if 'delta' in chunk_data and len(chunk_data['delta']) > 0:
                content_text = chunk_data['delta']['text']
                
                yield f"data: {json.dumps({'text': content_text})}\n\n"
                await asyncio.sleep(0)
    
    
    # 스트림 종료 신호
    yield f"data: {json.dumps({'done': True})}\n\n"

@app.post("/api/chat/stream")
async def stream_chat(request: ChatRequest):
    try:
        print("receive request")
        return StreamingResponse(
            generate_bedrock_stream(request.prompt, request.systemPrompt),
            media_type="text/event-stream"
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"ValueError: {str(e)}")
        
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.post("/api/chat/single")
async def chat(request: ChatRequest):
    try:    
        # Bedrock 클라이언트 초기화
        bedrock_runtime = boto3.client(
            service_name='bedrock-runtime',
            region_name='ap-northeast-2'  # 사용 중인 리전
        )
        
        # 페이로드 구성
        payload = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 2000,
            "temperature": 0.2,
            "top_p": 0.2,
            "top_k": 50,
            "system": request.systemPrompt,
            "messages": [
                {
                    "role": "user", 
                    "content": request.prompt
                }
            ]
        }
        
        # 일반 모델 호출 (스트리밍 아님)
        response = bedrock_runtime.invoke_model(
            modelId='anthropic.claude-3-5-sonnet-20240620-v1:0',
            contentType="application/json",
            accept="application/json",
            body=json.dumps(payload)
        )
        
        # 응답 처리
        response_body = json.loads(response['body'].read())
        print(response_body)
        full_response = response_body['content'][0]['text']

        # USER_RESPONSE와 MODEL_DATA 분리
        user_response = ""
        model_data = ""
        
        if "<USER_RESPONSE>" in full_response and "</USER_RESPONSE>" in full_response:
            user_response_match = re.search(r'<USER_RESPONSE>(.*?)</USER_RESPONSE>', full_response, re.DOTALL)
            if user_response_match:
                user_response = user_response_match.group(1).strip()
        
        if "<MODEL_DATA>" in full_response and "</MODEL_DATA>" in full_response:
            model_data_match = re.search(r'<MODEL_DATA>(.*?)</MODEL_DATA>', full_response, re.DOTALL)
            if model_data_match:
                model_data_str = model_data_match.group(1).strip()
                try:
                    # JSON 문자열을 파싱
                    model_data = json.loads(model_data_str)
                except json.JSONDecodeError:
                    # JSON 파싱에 실패하면 문자열 그대로 사용
                    model_data = model_data_str

        print(user_response)
        print(model_data)
        
        # 결과 반환
        return {
            "answer": user_response,
            "presignedUrls": []  # 필요한 경우 URL을 추가할 수 있습니다
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"ValueError: {str(e)}")
        
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

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