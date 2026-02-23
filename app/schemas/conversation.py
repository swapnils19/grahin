from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from uuid import UUID


class MessageBase(BaseModel):
    content: str


class MessageCreate(MessageBase):
    related_files: Optional[List[UUID]] = []


class MessageResponse(BaseModel):
    id: UUID
    role: str
    content: str
    created_at: datetime
    related_files: Optional[List[UUID]] = []

    class Config:
        from_attributes = True


class ConversationBase(BaseModel):
    title: Optional[str] = None


class ConversationCreate(ConversationBase):
    pass


class ConversationUpdate(BaseModel):
    title: Optional[str] = None


class ConversationResponse(ConversationBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
    messages: List[MessageResponse] = []

    class Config:
        from_attributes = True


class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[UUID] = None
    related_files: Optional[List[UUID]] = []


class ChatResponse(BaseModel):
    message: str
    conversation_id: UUID
    message_id: UUID
