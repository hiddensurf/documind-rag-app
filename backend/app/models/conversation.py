from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class Message(BaseModel):
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: str
    has_mindmap: bool = False
    mermaid_code: Optional[str] = None
    sources: Optional[List[str]] = None

class Conversation(BaseModel):
    id: str
    title: str
    created_at: str
    updated_at: str
    messages: List[Message] = []
    document_ids: List[str] = []

class CreateConversationRequest(BaseModel):
    document_ids: Optional[List[str]] = []

class UpdateConversationTitleRequest(BaseModel):
    title: str
