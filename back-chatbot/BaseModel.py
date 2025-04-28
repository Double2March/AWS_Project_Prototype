from uuid import UUID
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

class ChatMessage(BaseModel):
    message: str
    username: str
    timestamp: str

class ChatResponse(BaseModel):
    firstLambdaResult: str
    presignedUrls: Optional[List[str]] = None

class ChatRequest(BaseModel):
    uid : UUID
    prompt: str
    systemPrompt: str
    timestamp: datetime