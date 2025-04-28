import re
import json
import boto3
import traceback
from fastapi import APIRouter, HTTPException
from BaseModel import ChatRequest

router = APIRouter()

@router.post("/api/chat/single")
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