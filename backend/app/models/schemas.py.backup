from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class DocumentUploadResponse(BaseModel):
    id: str
    name: str
    size: int
    upload_date: str
    status: str = "processed"
    message: str = "Document uploaded and indexed successfully"

class ChatRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=1000)
    document_ids: Optional[List[str]] = None
    conversation_history: Optional[List[dict]] = None

class ChatResponse(BaseModel):
    response: str
    has_mindmap: bool = False
    mermaid_code: Optional[str] = None
    sources: Optional[List[str]] = None
    timestamp: str

class DocumentInfo(BaseModel):
    id: str
    name: str
    size: int
    upload_date: str
    status: str

class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
