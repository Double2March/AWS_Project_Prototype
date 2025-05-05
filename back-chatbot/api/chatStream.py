import json
import boto3
import traceback
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from BaseModel import ChatRequest

router = APIRouter()

@router.post("/api/chat/stream")
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