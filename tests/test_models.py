"""
Database model tests for Grahin RAG Application
"""
import pytest
import uuid
from datetime import datetime

from app.models import User, File, DocumentChunk, Conversation, Message, UserSession
from app.core.security import get_password_hash


class TestUserModel:
    """Test User model"""
    
    def test_create_user(self, db_session):
        """Test creating a user"""
        user = User(
            email="test@example.com",
            password_hash=get_password_hash("password"),
            full_name="Test User"
        )
        db_session.add(user)
        db_session.commit()
        
        assert user.id is not None
        assert user.email == "test@example.com"
        assert user.full_name == "Test User"
        assert user.is_active is True
        assert user.created_at is not None
    
    def test_user_relationships(self, db_session):
        """Test user relationships"""
        user = User(
            email="test@example.com",
            password_hash=get_password_hash("password")
        )
        db_session.add(user)
        db_session.commit()
        
        # Create related file
        file = File(
            user_id=user.id,
            filename="test.pdf",
            original_filename="original.pdf",
            file_type="pdf",
            file_size=1024,
            file_path="/uploads/test.pdf"
        )
        db_session.add(file)
        
        # Create related conversation
        conversation = Conversation(
            user_id=user.id,
            title="Test Conversation"
        )
        db_session.add(conversation)
        
        db_session.commit()
        
        # Test relationships
        assert len(user.files) == 1
        assert len(user.conversations) == 1
        assert user.files[0].filename == "test.pdf"
        assert user.conversations[0].title == "Test Conversation"


class TestFileModel:
    """Test File model"""
    
    def test_create_file(self, db_session, test_user):
        """Test creating a file"""
        file = File(
            user_id=test_user.id,
            filename="test.pdf",
            original_filename="original.pdf",
            file_type="pdf",
            file_size=1024,
            file_path="/uploads/test.pdf"
        )
        db_session.add(file)
        db_session.commit()
        
        assert file.id is not None
        assert file.user_id == test_user.id
        assert file.filename == "test.pdf"
        assert file.processing_status == "pending"
        assert file.is_processed is False
    
    def test_file_relationships(self, db_session, test_user):
        """Test file relationships"""
        file = File(
            user_id=test_user.id,
            filename="test.pdf",
            original_filename="original.pdf",
            file_type="pdf",
            file_size=1024,
            file_path="/uploads/test.pdf"
        )
        db_session.add(file)
        db_session.commit()
        
        # Create document chunk
        chunk = DocumentChunk(
            file_id=file.id,
            chunk_index=0,
            content="Test content"
        )
        db_session.add(chunk)
        db_session.commit()
        
        # Test relationships
        assert len(file.chunks) == 1
        assert file.chunks[0].content == "Test content"
        assert file.user.email == test_user.email


class TestDocumentChunkModel:
    """Test DocumentChunk model"""
    
    def test_create_chunk(self, db_session, test_file):
        """Test creating a document chunk"""
        chunk = DocumentChunk(
            file_id=test_file.id,
            chunk_index=0,
            content="Test chunk content",
            embedding_id=f"{test_file.id}_0"
        )
        db_session.add(chunk)
        db_session.commit()
        
        assert chunk.id is not None
        assert chunk.file_id == test_file.id
        assert chunk.chunk_index == 0
        assert chunk.content == "Test chunk content"
        assert chunk.embedding_id == f"{test_file.id}_0"


class TestConversationModel:
    """Test Conversation model"""
    
    def test_create_conversation(self, db_session, test_user):
        """Test creating a conversation"""
        conversation = Conversation(
            user_id=test_user.id,
            title="Test Conversation"
        )
        db_session.add(conversation)
        db_session.commit()
        
        assert conversation.id is not None
        assert conversation.user_id == test_user.id
        assert conversation.title == "Test Conversation"
        assert conversation.created_at is not None
    
    def test_conversation_relationships(self, db_session, test_user):
        """Test conversation relationships"""
        conversation = Conversation(
            user_id=test_user.id,
            title="Test Conversation"
        )
        db_session.add(conversation)
        db_session.commit()
        
        # Create message
        message = Message(
            conversation_id=conversation.id,
            role="user",
            content="Hello, world!"
        )
        db_session.add(message)
        db_session.commit()
        
        # Test relationships
        assert len(conversation.messages) == 1
        assert conversation.messages[0].content == "Hello, world!"
        assert conversation.user.email == test_user.email


class TestMessageModel:
    """Test Message model"""
    
    def test_create_message(self, db_session, test_conversation):
        """Test creating a message"""
        message = Message(
            conversation_id=test_conversation.id,
            role="user",
            content="Test message"
        )
        db_session.add(message)
        db_session.commit()
        
        assert message.id is not None
        assert message.conversation_id == test_conversation.id
        assert message.role == "user"
        assert message.content == "Test message"
        assert message.created_at is not None
    
    def test_message_with_related_files(self, db_session, test_conversation, test_file):
        """Test message with related files"""
        message = Message(
            conversation_id=test_conversation.id,
            role="user",
            content="Check this file",
            related_files=[test_file.id]
        )
        db_session.add(message)
        db_session.commit()
        
        assert len(message.related_files) == 1
        assert message.related_files[0] == test_file.id


class TestUserSessionModel:
    """Test UserSession model"""
    
    def test_create_session(self, db_session, test_user):
        """Test creating a user session"""
        from datetime import datetime, timedelta
        
        session = UserSession(
            user_id=test_user.id,
            token_hash="hashed_token",
            expires_at=datetime.utcnow() + timedelta(hours=1)
        )
        db_session.add(session)
        db_session.commit()
        
        assert session.id is not None
        assert session.user_id == test_user.id
        assert session.token_hash == "hashed_token"
        assert session.created_at is not None
    
    def test_session_relationships(self, db_session, test_user):
        """Test session relationships"""
        session = UserSession(
            user_id=test_user.id,
            token_hash="hashed_token",
            expires_at=datetime.utcnow()
        )
        db_session.add(session)
        db_session.commit()
        
        assert session.user.email == test_user.email
