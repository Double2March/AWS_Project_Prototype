import re
import json
import boto3
import traceback
import asyncio

from datetime import datetime
from fastapi import APIRouter, HTTPException

from BaseModel import ChatRequest
from service.dynamoService import get_model_data
from service.bedrockService import get_bedrock_response

router = APIRouter()

@router.post("/api/chat/bedrock")
async def chat(request: ChatRequest):
    print("bedrock logic 호출")
    try:
        # dynamodb 데이터 호출
        print(f"유저 uuid : {request.uid}")
        model_result = get_model_data(request.uid)

        print(f"최신 dynamodb model_result : {model_result}")

        get_response = get_bedrock_response(model_result)
        print(f"bedrock 로직 : {get_response}")

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