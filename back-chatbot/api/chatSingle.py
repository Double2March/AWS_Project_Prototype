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

        #A모델 max_tokens : 2500 / USER_RESPONSE, MODEL_DATA
        #B모델 max_tokens : 2500 / 
        #C모델 max_tokens : 4000 / files [filename, content]
        #D모델 max_tokens : 2000 / visual_tree
        #E모델 max_tokens : 4000 / project_name, 
        #                          source_files[file_path,content], 
        #                          build_configuration[file_path,content]
        #                          build_configuration[file_path,content]
        #F모델 max_tokens : 3500 / USER_RESPONSE[file_name, content]
        #                          PROVISIONING_SCRIPTS[file_path,content]
        #                          BUILD_SCRIPTS[file_path,content]
        
        #modelA = await invoke_bedrock_model(4000, model_a_sysPrompt, model_a_input) 
        #modelC = await invoke_bedrock_model(4000, model_c_sysPrompt, model_c_input) 
        #modelD = await invoke_bedrock_model(4000, model_d_sysPrompt, model_d_input)
        #modelE = await invoke_bedrock_model(4000, model_e_sysPrompt, model_e_input)
        #modelF = await invoke_bedrock_model(4000, model_f_sysPrompt, model_f_input)
        #get_response = await invoke_bedrock_logic()

        # 결과 반환
        return {
            "answer": "답변입니다.",
            "presignedUrls": ["https://idea-maker.s3.amazonaws.com/images-removebg-preview.zip?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIAZY46MTYWS6QPRRPO%2F20250430%2Fap-northeast-2%2Fs3%2Faws4_request&X-Amz-Date=20250430T090532Z&X-Amz-Expires=3600&X-Amz-SignedHeaders=host&X-Amz-Signature=902dd829f45742f9c24a7727b224d99f1d30ac6cac442e249f318a30ed38ad0d"]
        }
        
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