import re
import json
import boto3
import traceback
import asyncio

from datetime import datetime
from fastapi import APIRouter, HTTPException

from BaseModel import ChatRequest
from service.dynamoService import put_model_data, get_model_data
from service.bedrockService import invoke_bedrock_model

router = APIRouter()

@router.post("/api/chat/single")
async def chat(request: ChatRequest):
    print("호출")
    try:
        # user_response, model_data 변수 생성성
        user_response = ""
        model_data = ""
        temp_model_data = ""
        response_body=""

        # dynamoDB에 데이터 추가
        #put_model_data(request.uid, request.timestamp, model_data)

        # 데이터 호출 테스트
        #temp_model_data = get_model_data(request.uid)

        get_response = get_bedrock_response(model_result)

        # 결과 반환
        return get_response
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"ValueError: {str(e)}")
        
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

    except ValidationError as e:
        # Pydantic 모델 유효성 검사 실패 시
        raise HTTPException(status_code=422, detail=f"Validation error: {e.errors()}")

    except Exception as e:
        # 다른 예외 처리
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")