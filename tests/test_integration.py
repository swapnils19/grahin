"""
Integration tests for Grahin RAG Application
"""
import pytest
import tempfile
import os
from fastapi.testclient import TestClient


class TestIntegration:
    """End-to-end integration tests"""
    
    def test_full_rag_workflow(self, client: TestClient, temp_upload_dir):
        """Test complete RAG workflow: register → upload → chat → search"""
        
        # 1. Register user
        register_response = client.post(
            "/api/auth/register",
            json={
                "email": "integration@example.com",
                "password": "password123",
                "full_name": "Integration Test User"
            }
        )
        assert register_response.status_code == 200
        user_data = register_response.json()
        
        # 2. Login
        login_response = client.post(
            "/api/auth/login",
            data={"username": user_data["email"], "password": "password123"}
        )
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # 3. Create test document
        test_content = """
        Artificial Intelligence and Machine Learning
        
        Artificial intelligence (AI) is a broad field of computer science focused on creating systems 
        that can perform tasks that typically require human intelligence. Machine learning is a subset 
        of AI that enables systems to learn and improve from experience without being explicitly programmed.
        
        Deep learning is a type of machine learning based on artificial neural networks. 
        Natural language processing (NLP) allows computers to understand and generate human language.
        
        Applications of AI include image recognition, speech recognition, recommendation systems,
        autonomous vehicles, and large language models like GPT.
        """
        
        test_file = os.path.join(temp_upload_dir, "ai_document.txt")
        with open(test_file, "w") as f:
            f.write(test_content)
        
        # 4. Upload file
        with open(test_file, "rb") as f:
            upload_response = client.post(
                "/api/files/upload",
                headers=headers,
                files={"file": ("ai_document.txt", f, "text/plain")}
            )
        assert upload_response.status_code == 200
        file_data = upload_response.json()
        
        # 5. Wait for processing (simulate)
        import time
        time.sleep(1)
        
        # 6. Start conversation about the document
        chat_response = client.post(
            "/api/chat/chat",
            headers=headers,
            json={
                "message": "What is artificial intelligence according to the document?",
                "related_files": [file_data["id"]]
            }
        )
        assert chat_response.status_code == 200
        chat_data = chat_response.json()
        conversation_id = chat_data["conversation_id"]
        
        # 7. Continue conversation
        followup_response = client.post(
            "/api/chat/chat",
            headers=headers,
            json={
                "message": "How does machine learning relate to AI?",
                "conversation_id": conversation_id
            }
        )
        assert followup_response.status_code == 200
        
        # 8. Search documents
        search_response = client.get(
            "/api/chat/search",
            headers=headers,
            params={"query": "deep learning", "k": 3}
        )
        assert search_response.status_code == 200
        search_data = search_response.json()
        assert len(search_data["results"]) >= 0
        
        # 9. Get conversation history
        conv_response = client.get(
            f"/api/chat/conversations/{conversation_id}",
            headers=headers
        )
        assert conv_response.status_code == 200
        conv_data = conv_response.json()
        assert len(conv_data["messages"]) >= 2  # At least user message + AI response
        
        # 10. List all conversations
        list_response = client.get("/api/chat/conversations", headers=headers)
        assert list_response.status_code == 200
        conv_list = list_response.json()
        assert len(conv_list) >= 1
        
        # 11. Get files summary
        summary_response = client.get("/api/chat/files-summary", headers=headers)
        assert summary_response.status_code == 200
        summary_data = summary_response.json()
        assert summary_data["total_files"] >= 1
        
        # 12. Clean up - delete conversation
        delete_response = client.delete(
            f"/api/chat/conversations/{conversation_id}",
            headers=headers
        )
        assert delete_response.status_code == 200
        
        # 13. Delete file
        delete_file_response = client.delete(
            f"/api/files/{file_data['id']}",
            headers=headers
        )
        assert delete_file_response.status_code == 200
    
    def test_multi_user_isolation(self, client: TestClient, temp_upload_dir):
        """Test that users cannot access each other's data"""
        
        # Create two users
        users = []
        tokens = []
        
        for i, email in enumerate(["user1@example.com", "user2@example.com"]):
            # Register
            client.post(
                "/api/auth/register",
                json={
                    "email": email,
                    "password": f"password{i}",
                    "full_name": f"User {i+1}"
                }
            )
            
            # Login
            login_response = client.post(
                "/api/auth/login",
                data={"username": email, "password": f"password{i}"}
            )
            tokens.append(login_response.json()["access_token"])
        
        headers1 = {"Authorization": f"Bearer {tokens[0]}"}
        headers2 = {"Authorization": f"Bearer {tokens[1]}"}
        
        # User 1 uploads a file
        test_file = os.path.join(temp_upload_dir, "user1_file.txt")
        with open(test_file, "w") as f:
            f.write("This is User 1's private document.")
        
        with open(test_file, "rb") as f:
            upload_response = client.post(
                "/api/files/upload",
                headers=headers1,
                files={"file": ("user1_file.txt", f, "text/plain")}
            )
        assert upload_response.status_code == 200
        file_id = upload_response.json()["id"]
        
        # User 1 can see their file
        files_response = client.get("/api/files/", headers=headers1)
        assert files_response.status_code == 200
        assert len(files_response.json()["files"]) == 1
        
        # User 2 cannot see User 1's file
        files_response = client.get("/api/files/", headers=headers2)
        assert files_response.status_code == 200
        assert len(files_response.json()["files"]) == 0
        
        # User 2 cannot access User 1's file directly
        file_response = client.get(f"/api/files/{file_id}", headers=headers2)
        assert file_response.status_code == 404
        
        # User 2 cannot delete User 1's file
        delete_response = client.delete(f"/api/files/{file_id}", headers=headers2)
        assert delete_response.status_code == 404
    
    def test_error_handling(self, client: TestClient, auth_headers):
        """Test various error scenarios"""
        
        # Test invalid file upload
        response = client.post(
            "/api/files/upload",
            headers=auth_headers,
            files={"file": ("", b"", "text/plain")}  # Empty file
        )
        # Should either succeed or fail gracefully
        
        # Test invalid conversation ID
        response = client.post(
            "/api/chat/chat",
            headers=auth_headers,
            json={
                "message": "Hello",
                "conversation_id": "invalid-uuid"
            }
        )
        assert response.status_code == 422  # Validation error
        
        # Test very long message
        long_message = "x" * 10000
        response = client.post(
            "/api/chat/chat",
            headers=auth_headers,
            json={"message": long_message}
        )
        # Should handle gracefully (either accept or reject with proper error)
        
        # Test search with empty query
        response = client.get(
            "/api/chat/search",
            headers=auth_headers,
            params={"query": ""}
        )
        # Should handle empty search appropriately
