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