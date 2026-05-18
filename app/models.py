from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class ChatRequest(BaseModel):
    session_id: str = Field(..., description="Unique session identifier")
    message: str = Field(..., description="User message")
    use_rag: Optional[bool] = Field(default=None, description="Whether to use RAG. If None, auto-detect.")
    use_agent: Optional[bool] = Field(default=None, description="Whether to use agent. If None, auto-detect.")

class ChatResponse(BaseModel):
    session_id: str
    message: str
    
class UploadResponse(BaseModel):
    filename: str
    status: str
    chunks: int
    message: str

class DebugSearchRequest(BaseModel):
    query: str = Field(..., description="Search query")
    top_k: int = Field(default=5, description="Number of results to return")

class DebugSearchResponse(BaseModel):
    query: str
    top_k: int
    results: List[Dict[str, Any]]
