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
    query: Optional[str] = Field(None, min_length=1, max_length=1000)  # Optional for compatibility
    message: Optional[str] = Field(None, min_length=1, max_length=1000)  # New field name
    document_ids: Optional[List[str]] = None
    conversation_history: Optional[List[dict]] = None
    model: Optional[str] = None  # Allow model selection
    
    @property
    def get_query(self) -> str:
        """Get query from either 'query' or 'message' field"""
        return self.message or self.query or ""

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
