"""
Chat and RAG functionality tests for Grahin RAG Application
"""
import pytest
from fastapi.testclient import TestClient


class TestChat:
    """Test chat and RAG endpoints"""
    
    def test_chat_new_conversation(self, client: TestClient, auth_headers, test_chunk):
        """Test starting a new chat conversation"""
        response = client.post(
            "/api/chat/chat",
            headers=auth_headers,
            json={
                "message": "What can you tell me about artificial intelligence?",
                "related_files": [str(test_chunk.file_id)]
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "conversation_id" in data
        assert "message_id" in data
        assert len(data["message"]) > 0
    
    def test_chat_existing_conversation(self, client: TestClient, auth_headers, test_conversation):
        """Test continuing an existing conversation"""
        response = client.post(
            "/api/chat/chat",
            headers=auth_headers,
            json={
                "message": "Can you explain more about machine learning?",
                "conversation_id": str(test_conversation.id)
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["conversation_id"] == str(test_conversation.id)
        assert "message" in data
    
    def test_chat_unauthorized(self, client: TestClient):
        """Test chat without authentication"""
        response = client.post(
            "/api/chat/chat",
            json={"message": "Hello?"}
        )
        
        assert response.status_code == 401
    
    def test_list_conversations(self, client: TestClient, auth_headers, test_conversation):
        """Test listing user conversations"""
        response = client.get("/api/chat/conversations", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        
        # Check conversation structure
        conv = data[0]
        assert "id" in conv
        assert "title" in conv
        assert "created_at" in conv
    
    def test_list_conversations_unauthorized(self, client: TestClient):
        """Test listing conversations without authentication"""
        response = client.get("/api/chat/conversations")
        
        assert response.status_code == 401
    
    def test_get_conversation(self, client: TestClient, auth_headers, test_conversation):
        """Test getting specific conversation with messages"""
        response = client.get(
            f"/api/chat/conversations/{test_conversation.id}", 
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(test_conversation.id)
        assert "messages" in data
        assert isinstance(data["messages"], list)
    
    def test_get_conversation_not_found(self, client: TestClient, auth_headers):
        """Test getting non-existent conversation"""
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = client.get(f"/api/chat/conversations/{fake_id}", headers=auth_headers)
        
        assert response.status_code == 404
    
    def test_get_other_user_conversation(self, client: TestClient, db_session):
        """Test getting another user's conversation (should fail)"""
        # Create another user and conversation
        from app.core.security import get_password_hash
        from app.models import User, Conversation
        import uuid
        
        other_user = User(
            email="other@example.com",
            password_hash=get_password_hash("password"),
            full_name="Other User"
        )
        db_session.add(other_user)
        db_session.commit()
        
        other_conv = Conversation(
            user_id=other_user.id,
            title="Other Conversation"
        )
        db_session.add(other_conv)
        db_session.commit()
        
        # Login as first user and try to access other user's conversation
        response = client.post(
            "/api/auth/login",
            data={"username": "test@example.com", "password": "testpassword"}
        )
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.get(f"/api/chat/conversations/{other_conv.id}", headers=headers)
        assert response.status_code == 404
    
    def test_search_documents(self, client: TestClient, auth_headers, test_chunk):
        """Test document search functionality"""
        response = client.get(
            "/api/chat/search",
            headers=auth_headers,
            params={"query": "artificial intelligence", "k": 5}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert isinstance(data["results"], list)
    
    def test_search_unauthorized(self, client: TestClient):
        """Test search without authentication"""
        response = client.get("/api/chat/search?query=test")
        
        assert response.status_code == 401
    
    def test_files_summary(self, client: TestClient, auth_headers, test_file, test_chunk):
        """Test getting files summary"""
        response = client.get("/api/chat/files-summary", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "total_files" in data
        assert "total_chunks" in data
        assert "files" in data
        assert isinstance(data["files"], list)
        assert data["total_files"] >= 1
        assert data["total_chunks"] >= 1
    
    def test_files_summary_unauthorized(self, client: TestClient):
        """Test files summary without authentication"""
        response = client.get("/api/chat/files-summary")
        
        assert response.status_code == 401
    
    def test_delete_conversation(self, client: TestClient, auth_headers, test_conversation):
        """Test deleting a conversation"""
        response = client.delete(
            f"/api/chat/conversations/{test_conversation.id}", 
            headers=auth_headers
        )
        
        assert response.status_code == 200
        assert "deleted successfully" in response.json()["message"].lower()
        
        # Verify conversation is deleted
        response = client.get(
            f"/api/chat/conversations/{test_conversation.id}", 
            headers=auth_headers
        )
        assert response.status_code == 404
    
    def test_delete_conversation_unauthorized(self, client: TestClient, test_conversation):
        """Test deleting conversation without authentication"""
        response = client.delete(f"/api/chat/conversations/{test_conversation.id}")
        
        assert response.status_code == 401
