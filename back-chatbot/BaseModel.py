from typing import List, Optional
from pydantic import BaseModel

# 사용자에게 받는 값
class ChatMessage(BaseModel):
    message: str
    username: str
    timestamp: str

class ChatResponse(BaseModel):
    firstLambdaResult: str
    presignedUrls: Optional[List[str]] = None

class ChatRequest(BaseModel):
    prompt: str
    systemPrompt: str
    timestamp: str