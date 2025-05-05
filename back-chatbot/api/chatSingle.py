import re
import json
import boto3
import traceback
import asyncio

from datetime import datetime
from fastapi import APIRouter, HTTPException

from prompt.prompt_a import systemPrompt as model_a_sysPrompt

from BaseModel import ChatRequest
from service.dynamoService import put_model_data
from service.bedrockService import invoke_userReponse
from service.websocketService import send_to_websocket

router = APIRouter()

@router.post("/api/chat/single")
async def chat(request: ChatRequest):
    try:    

        text_data = invoke_userReponse(2000,model_a_sysPrompt,request.prompt )

        # USER_RESPONSE와 MODEL_DATA 분리
        user_response, model_result = extract_sections(text_data)          

        # dynamoDB에 데이터 추가
        put_model_data(request.uid, request.timestamp, model_result)
        
        # 결과 반환
        return {
            "answer": user_response,
            "create" : True
        }
        
    except ValueError as e:
        return {
            "answer": text_data,
            "create" : False
        }
        raise HTTPException(status_code=400, detail=f"ValueError: {str(e)}")
        
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

def extract_sections(text):
    try:
        # USER_SECTION 추출
        user_section_pattern = r'===USER_SECTION===\s*([\s\S]*?)\s*===USER_SECTION_END==='
        user_section_match = re.search(user_section_pattern, text)
        
        if not user_section_match:
            raise ValueError("USER_SECTION을 찾을 수 없습니다.")
            
        user_response = user_section_match.group(1).strip()
        
        # MODEL_SECTION 추출
        model_section_pattern = r'===MODEL_SECTION_START===\s*([\s\S]*?)\s*===MODEL_SECTION_END==='
        model_section_match = re.search(model_section_pattern, text)
        
        if not model_section_match:
            raise ValueError("MODEL_SECTION을 찾을 수 없습니다.")
            
        model_result = model_section_match.group(1).strip()
        
        return user_response, model_result
        
    except Exception as e:
        send_to_websocket(f"섹션 추출 중 오류 발생: {str(e)}", "ERROR")
        # 원래 예외를 다시 발생시켜 상위 핸들러가 처리할 수 있도록 함
        raise