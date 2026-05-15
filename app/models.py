from pydantic import BaseModel, Field
from typing import Optional

class ChatRequest(BaseModel):
    session_id: str = Field(..., description="Unique session identifier")
    message: str = Field(..., description="User message")

class ChatResponse(BaseModel):
    session_id: str
    message: str
    
class UploadResponse(BaseModel):
    filename: str
    status: str
    chunks: int
