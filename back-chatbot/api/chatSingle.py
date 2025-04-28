import re
import json
import boto3
import traceback
from fastapi import APIRouter, HTTPException

from BaseModel import ChatRequest
from api.dynamoService import put_model_data, get_model_data
from datetime import datetime

router = APIRouter()

@router.post("/api/chat/single")
async def chat(request: ChatRequest):
    try:
        # user_response, model_data 변수 생성성
        user_response = ""
        model_data = ""
        temp_model_data = ""

        # Bedrock 클라이언트 초기화
        bedrock_runtime = boto3.client(
            service_name='bedrock-runtime',
            region_name='ap-northeast-2'  # 사용 중인 리전
        )
        
        # 페이로드 구성
        payload = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 2500,
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
        
        # 일반 모델 호출
        response = bedrock_runtime.invoke_model(
            modelId='anthropic.claude-3-5-sonnet-20240620-v1:0',
            contentType="application/json",
            accept="application/json",
            body=json.dumps(payload)
        )
        
        try:
            response_body = json.loads(response['body'].read()) 
            text_data = response_body['content'][0]['text']
            parsed_data = json.loads(text_data)
            user_response = parsed_data['USER_RESPONSE']
            model_data = parsed_data['MODEL_DATA']

        except json.JSONDecodeError as e:
            print(f"JSON 파싱 오류: {e}")   
            # 줄 번호와 위치 확인
            print(f"오류 위치: 줄 {e.lineno}, 컬럼 {e.colno}")
            print(f"오류 부분: {e.doc[e.pos-20:e.pos+20]}")
        except:
            user_response = ""
            model_data = ""
            print("json 파싱 실패")

        # dynamoDB에 데이터 추가
        #put_model_data(request.uid, request.timestamp, model_data)

        # 데이터 호출 테스트
        #temp_model_data = get_model_data(request.uid)
        print(temp_model_data)
      
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

    except ValidationError as e:
        # Pydantic 모델 유효성 검사 실패 시
        raise HTTPException(status_code=422, detail=f"Validation error: {e.errors()}")

    except Exception as e:
        # 다른 예외 처리
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")