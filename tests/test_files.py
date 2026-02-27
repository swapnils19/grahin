"""
File management tests for Grahin RAG Application
"""
import pytest
import os
from fastapi.testclient import TestClient


class TestFiles:
    """Test file management endpoints"""
    
    def test_upload_file(self, client: TestClient, auth_headers, sample_text_file):
        """Test file upload"""
        with open(sample_text_file, "rb") as f:
            response = client.post(
                "/api/files/upload",
                headers=auth_headers,
                files={"file": ("test.txt", f, "text/plain")}
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["original_filename"] == "test.txt"
        assert data["file_type"] == "text"
        assert data["processing_status"] in ["pending", "completed"]
        assert "id" in data
        assert "upload_date" in data
    
    def test_upload_file_unauthorized(self, client: TestClient, sample_text_file):
        """Test file upload without authentication"""
        with open(sample_text_file, "rb") as f:
            response = client.post(
                "/api/files/upload",
                files={"file": ("test.txt", f, "text/plain")}
            )
        
        assert response.status_code == 401
    
    def test_list_files(self, client: TestClient, auth_headers, test_file):
        """Test listing user files"""
        response = client.get("/api/files/", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "files" in data
        assert "total" in data
        assert len(data["files"]) >= 1
        assert data["total"] >= 1
    
    def test_list_files_unauthorized(self, client: TestClient):
        """Test listing files without authentication"""
        response = client.get("/api/files/")
        
        assert response.status_code == 401
    
    def test_get_file(self, client: TestClient, auth_headers, test_file):
        """Test getting specific file"""
        response = client.get(f"/api/files/{test_file.id}", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(test_file.id)
        assert data["original_filename"] == test_file.original_filename
    
    def test_get_file_unauthorized(self, client: TestClient, test_file):
        """Test getting file without authentication"""
        response = client.get(f"/api/files/{test_file.id}")
        
        assert response.status_code == 401
    
    def test_get_file_not_found(self, client: TestClient, auth_headers):
        """Test getting non-existent file"""
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = client.get(f"/api/files/{fake_id}", headers=auth_headers)
        
        assert response.status_code == 404
    
    def test_get_other_user_file(self, client: TestClient, db_session):
        """Test getting another user's file (should fail)"""
        # Create another user
        from app.core.security import get_password_hash
        from app.models import User, File
        import uuid
        
        other_user = User(
            email="other@example.com",
            password_hash=get_password_hash("password"),
            full_name="Other User"
        )
        db_session.add(other_user)
        db_session.commit()
        
        other_file = File(
            user_id=other_user.id,
            filename="other_file.pdf",
            original_filename="other.pdf",
            file_type="pdf",
            file_size=1024,
            file_path="/uploads/other.pdf"
        )
        db_session.add(other_file)
        db_session.commit()
        
        # Login as first user and try to access other user's file
        response = client.post(
            "/api/auth/login",
            data={"username": "test@example.com", "password": "testpassword"}
        )
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.get(f"/api/files/{other_file.id}", headers=headers)
        assert response.status_code == 404  # Should not find other user's file
    
    def test_delete_file(self, client: TestClient, auth_headers, test_file):
        """Test deleting a file"""
        response = client.delete(f"/api/files/{test_file.id}", headers=auth_headers)
        
        assert response.status_code == 200
        assert "deleted successfully" in response.json()["message"].lower()
        
        # Verify file is deleted
        response = client.get(f"/api/files/{test_file.id}", headers=auth_headers)
        assert response.status_code == 404
    
    def test_delete_file_unauthorized(self, client: TestClient, test_file):
        """Test deleting file without authentication"""
        response = client.delete(f"/api/files/{test_file.id}")
        
        assert response.status_code == 401
    
    def test_delete_file_not_found(self, client: TestClient, auth_headers):
        """Test deleting non-existent file"""
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = client.delete(f"/api/files/{fake_id}", headers=auth_headers)
        
        assert response.status_code == 404
