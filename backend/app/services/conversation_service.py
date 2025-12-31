import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Optional
import logging
from app.core.config import get_settings
from app.models.conversation import Conversation, Message

logger = logging.getLogger(__name__)
settings = get_settings()

class ConversationService:
    """Service for managing conversation history"""
    
    def __init__(self):
        self.data_dir = Path(settings.UPLOAD_DIR).parent / "conversations"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.conversations_file = self.data_dir / "conversations.json"
        self.conversations = self._load_conversations()
        logger.info(f"ConversationService initialized. Data dir: {self.data_dir}")
    
    def _load_conversations(self) -> dict:
        """Load conversations from file"""
        if self.conversations_file.exists():
            try:
                with open(self.conversations_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading conversations: {e}")
                return {}
        return {}
    
    def _save_conversations(self):
        """Save conversations to file"""
        try:
            with open(self.conversations_file, 'w') as f:
                json.dump(self.conversations, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving conversations: {e}")
    
    def _generate_title(self, first_message: str) -> str:
        """Generate a title from the first message"""
        title = first_message[:50]
        if len(first_message) > 50:
            title += "..."
        return title
    
    def create_conversation(self, document_ids: List[str] = None) -> Conversation:
        """Create a new conversation"""
        conv_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        
        conversation = {
            "id": conv_id,
            "title": "New Chat",
            "created_at": now,
            "updated_at": now,
            "messages": [],
            "document_ids": document_ids or []
        }
        
        self.conversations[conv_id] = conversation
        self._save_conversations()
        
        logger.info(f"Created conversation: {conv_id} with documents: {document_ids}")
        return Conversation(**conversation)
    
    def get_conversation(self, conv_id: str) -> Optional[Conversation]:
        """Get a conversation by ID"""
        conv = self.conversations.get(conv_id)
        if conv:
            return Conversation(**conv)
        return None
    
    def get_all_conversations(self) -> List[Conversation]:
        """Get all conversations sorted by updated_at"""
        conversations = [
            Conversation(**conv) 
            for conv in self.conversations.values()
        ]
        conversations.sort(
            key=lambda x: x.updated_at, 
            reverse=True
        )
        return conversations
    
    def add_message(
        self, 
        conv_id: str, 
        message: Message,
        auto_title: bool = True
    ) -> Optional[Conversation]:
        """Add a message to a conversation"""
        if conv_id not in self.conversations:
            return None
        
        conv = self.conversations[conv_id]
        
        message_dict = message.dict()
        conv["messages"].append(message_dict)
        conv["updated_at"] = datetime.now().isoformat()
        
        if auto_title and len(conv["messages"]) == 1 and message.role == "user":
            conv["title"] = self._generate_title(message.content)
        
        self._save_conversations()
        logger.info(f"Added message to conversation: {conv_id}")
        
        return Conversation(**conv)
    
    def update_title(self, conv_id: str, title: str) -> Optional[Conversation]:
        """Update conversation title"""
        if conv_id not in self.conversations:
            return None
        
        self.conversations[conv_id]["title"] = title
        self.conversations[conv_id]["updated_at"] = datetime.now().isoformat()
        self._save_conversations()
        
        logger.info(f"Updated title for conversation: {conv_id}")
        return Conversation(**self.conversations[conv_id])
    
    def update_documents(self, conv_id: str, document_ids: List[str]) -> Optional[Conversation]:
        """Update conversation documents"""
        if conv_id not in self.conversations:
            return None
        
        self.conversations[conv_id]["document_ids"] = document_ids
        self.conversations[conv_id]["updated_at"] = datetime.now().isoformat()
        self._save_conversations()
        
        logger.info(f"Updated documents for conversation: {conv_id} to {document_ids}")
        return Conversation(**self.conversations[conv_id])
    
    def delete_conversation(self, conv_id: str) -> bool:
        """Delete a conversation"""
        if conv_id in self.conversations:
            del self.conversations[conv_id]
            self._save_conversations()
            logger.info(f"Deleted conversation: {conv_id}")
            return True
        return False
    
    def get_conversation_messages(self, conv_id: str) -> List[Message]:
        """Get messages for a conversation"""
        conv = self.conversations.get(conv_id)
        if conv:
            return [Message(**msg) for msg in conv["messages"]]
        return []

conversation_service = ConversationService()
