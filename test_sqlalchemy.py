#!/usr/bin/env python3
"""
Test script to verify SQLAlchemy models work correctly
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from app.core.database import engine, Base, SessionLocal
from app.models import User, File, DocumentChunk, Conversation, Message, UserSession
import uuid

def test_models():
    """Test SQLAlchemy models"""
    print("🧪 Testing SQLAlchemy Models...")
    
    # Create all tables
    print("📋 Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tables created successfully!")
    
    # Test database session
    print("🔗 Testing database session...")
    db = SessionLocal()
    
    try:
        # Create a test user
        print("👤 Creating test user...")
        test_user = User(
            email="test@example.com",
            password_hash="hashed_password",
            full_name="Test User"
        )
        db.add(test_user)
        db.commit()
        db.refresh(test_user)
        print(f"✅ User created: {test_user.email}")
        
        # Create a test file
        print("📁 Creating test file...")
        test_file = File(
            user_id=test_user.id,
            filename="test_file.pdf",
            original_filename="original.pdf",
            file_type="pdf",
            file_size=1024,
            file_path="/uploads/test_file.pdf",
            mime_type="application/pdf"
        )
        db.add(test_file)
        db.commit()
        db.refresh(test_file)
        print(f"✅ File created: {test_file.filename}")
        
        # Create a test document chunk
        print("📄 Creating test document chunk...")
        test_chunk = DocumentChunk(
            file_id=test_file.id,
            chunk_index=0,
            content="This is a test document chunk for RAG processing.",
            embedding_id=f"{test_file.id}_0"
        )
        db.add(test_chunk)
        db.commit()
        db.refresh(test_chunk)
        print(f"✅ Chunk created: {test_chunk.content[:50]}...")
        
        # Create a test conversation
        print("💬 Creating test conversation...")
        test_conversation = Conversation(
            user_id=test_user.id,
            title="Test Conversation"
        )
        db.add(test_conversation)
        db.commit()
        db.refresh(test_conversation)
        print(f"✅ Conversation created: {test_conversation.title}")
        
        # Create a test message
        print("📨 Creating test message...")
        test_message = Message(
            conversation_id=test_conversation.id,
            role="user",
            content="What can you tell me about the uploaded document?",
            related_files=[test_file.id]
        )
        db.add(test_message)
        db.commit()
        db.refresh(test_message)
        print(f"✅ Message created: {test_message.content[:50]}...")
        
        # Test relationships
        print("🔗 Testing relationships...")
        user_with_files = db.query(User).filter(User.id == test_user.id).first()
        print(f"✅ User has {len(user_with_files.files)} files")
        print(f"✅ User has {len(user_with_files.conversations)} conversations")
        
        file_with_chunks = db.query(File).filter(File.id == test_file.id).first()
        print(f"✅ File has {len(file_with_chunks.chunks)} chunks")
        
        conversation_with_messages = db.query(Conversation).filter(Conversation.id == test_conversation.id).first()
        print(f"✅ Conversation has {len(conversation_with_messages.messages)} messages")
        
        print("\n🎉 All SQLAlchemy tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        db.rollback()
        return False
        
    finally:
        db.close()

def test_pydantic_compatibility():
    """Test that SQLAlchemy models work with Pydantic"""
    print("\n🔧 Testing Pydantic compatibility...")
    
    from pydantic import BaseModel
    from typing import Optional
    from datetime import datetime
    
    # Create Pydantic schemas
    class UserResponse(BaseModel):
        id: uuid.UUID
        email: str
        full_name: Optional[str]
        created_at: datetime
        
        class Config:
            from_attributes = True
    
    class FileResponse(BaseModel):
        id: uuid.UUID
        filename: str
        file_type: str
        file_size: int
        
        class Config:
            from_attributes = True
    
    db = SessionLocal()
    
    try:
        # Get user from database
        user = db.query(User).first()
        if user:
            # Convert SQLAlchemy to Pydantic
            user_response = UserResponse.from_orm(user)
            print(f"✅ SQLAlchemy User → Pydantic: {user_response.email}")
        
        # Get file from database
        file = db.query(File).first()
        if file:
            file_response = FileResponse.from_orm(file)
            print(f"✅ SQLAlchemy File → Pydantic: {file_response.filename}")
        
        print("✅ Pydantic compatibility test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Pydantic compatibility test failed: {e}")
        return False
        
    finally:
        db.close()

def cleanup_test_data():
    """Clean up test data"""
    print("\n🧹 Cleaning up test data...")
    db = SessionLocal()
    
    try:
        # Delete in correct order (respect foreign keys)
        db.query(Message).delete()
        db.query(DocumentChunk).delete()
        db.query(File).delete()
        db.query(Conversation).delete()
        db.query(UserSession).delete()
        db.query(User).delete()
        db.commit()
        print("✅ Test data cleaned up!")
        
    except Exception as e:
        print(f"❌ Cleanup failed: {e}")
        db.rollback()
        
    finally:
        db.close()

if __name__ == "__main__":
    print("🚀 SQLAlchemy + Pydantic Integration Test")
    print("=" * 50)
    
    success = True
    
    # Test models
    if not test_models():
        success = False
    
    # Test Pydantic compatibility
    if not test_pydantic_compatibility():
        success = False
    
    # Clean up
    cleanup_test_data()
    
    if success:
        print("\n🎯 All tests passed! SQLAlchemy + Pydantic integration is working perfectly!")
        print("✨ Your RAG application is ready with the best of both worlds!")
    else:
        print("\n💥 Some tests failed. Please check the implementation.")
        sys.exit(1)
