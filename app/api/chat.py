import uuid
import pdb
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.models.user import User
from app.models.conversation import Conversation, Message
from app.models.file import File
from app.schemas.conversation import (
    ChatRequest, ChatResponse, ConversationCreate,
    ConversationResponse, ConversationUpdate
)
from app.api.deps import get_current_active_user
from app.services.rag_service import rag_service

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    pdb.set_trace()  # Debug FastAPI endpoint

    # Get or create conversation
    if request.conversation_id:
        conversation = db.query(Conversation).filter(
            Conversation.id == request.conversation_id,
            Conversation.user_id == current_user.id
        ).first()

        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
    else:
        # Create new conversation
        conversation = Conversation(
            user_id=current_user.id,
            title=request.message[:50] + "..." if len(request.message) > 50 else request.message
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)

    # Save user message
    user_message = Message(
        conversation_id=conversation.id,
        role="user",
        content=request.message,
        related_files=request.related_files or []
    )
    db.add(user_message)

    # Generate AI response using RAG
    try:
        ai_response = rag_service.generate_response(
            user_id=current_user.id,
            query=request.message,
            file_ids=request.related_files
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating response: {str(e)}"
        )

    # Save AI message
    ai_message = Message(
        conversation_id=conversation.id,
        role="assistant",
        content=ai_response
    )
    db.add(ai_message)

    # Update conversation timestamp
    from datetime import datetime
    conversation.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(ai_message)

    return ChatResponse(
        message=ai_response,
        conversation_id=conversation.id,
        message_id=ai_message.id
    )


@router.get("/conversations", response_model=List[ConversationResponse])
def list_conversations(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    conversations = db.query(Conversation).filter(
        Conversation.user_id == current_user.id
    ).order_by(Conversation.updated_at.desc()).all()

    return conversations


@router.get("/conversations/{conversation_id}", response_model=ConversationResponse)
def get_conversation(
    conversation_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    return conversation


@router.put("/conversations/{conversation_id}", response_model=ConversationResponse)
def update_conversation(
    conversation_id: uuid.UUID,
    conversation_update: ConversationUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    if conversation_update.title is not None:
        conversation.title = conversation_update.title

    db.commit()
    db.refresh(conversation)

    return conversation


@router.delete("/conversations/{conversation_id}")
def delete_conversation(
    conversation_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    db.delete(conversation)
    db.commit()

    return {"message": "Conversation deleted successfully"}


@router.get("/search")
def search_documents(
    query: str,
    k: int = 5,
    current_user: User = Depends(get_current_active_user)
):
    """Search for relevant documents in user's collection"""
    try:
        results = rag_service.search_documents(
            user_id=current_user.id,
            query=query,
            k=k
        )
        return {"results": results}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error searching documents: {str(e)}"
        )


@router.get("/files-summary")
def get_files_summary(
    current_user: User = Depends(get_current_active_user)
):
    """Get summary of user's uploaded files"""
    try:
        summary = rag_service.get_user_files_summary(current_user.id)
        return summary
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting files summary: {str(e)}"
        )
