import re
import json
import boto3
import traceback
import asyncio

from datetime import datetime
from fastapi import APIRouter, HTTPException

from BaseModel import CreateRequest
from service.dynamoService import get_model_data
from service.bedrockService import get_bedrock_response_async
from service.websocketService import send_to_websocket

router = APIRouter()

@router.post("/api/chat/createProject")
async def chat(request: CreateRequest):
    print("bedrock logic 호출")
    send_to_websocket("프로젝트 만들기 시작!")
    try:
        
        #호출 정보출력
        print(f"유저 uuid : {request.uid}")
        print(f"호출시간 : {request.timestamp}")


        # dynamodb 데이터 호출
        model_result = get_model_data(request.uid)
        print(f"최신 dynamodb model_result : {model_result}")

        get_response = await get_bedrock_response_async(model_result)
        print(f"bedrock 로직 : {get_response}")

        # 결과 반환
        return get_response
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"ValueError: {str(e)}")
        
    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()  # 상세 오류 추적
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")