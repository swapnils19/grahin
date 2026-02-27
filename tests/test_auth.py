"""
Authentication tests for Grahin RAG Application
"""
import pytest
from fastapi.testclient import TestClient


class TestAuth:
    """Test authentication endpoints"""
    
    def test_register_user(self, client: TestClient):
        """Test user registration"""
        response = client.post(
            "/api/auth/register",
            json={
                "email": "newuser@example.com",
                "password": "newpassword123",
                "full_name": "New User"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "newuser@example.com"
        assert data["full_name"] == "New User"
        assert "id" in data
        assert "created_at" in data
    
    def test_register_duplicate_email(self, client: TestClient, test_user):
        """Test registration with duplicate email"""
        response = client.post(
            "/api/auth/register",
            json={
                "email": test_user.email,
                "password": "password123",
                "full_name": "Duplicate User"
            }
        )
        
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"].lower()
    
    def test_login_success(self, client: TestClient, test_user):
        """Test successful login"""
        response = client.post(
            "/api/auth/login",
            data={"username": test_user.email, "password": "testpassword"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert len(data["access_token"]) > 10
    
    def test_login_invalid_credentials(self, client: TestClient, test_user):
        """Test login with invalid credentials"""
        response = client.post(
            "/api/auth/login",
            data={"username": test_user.email, "password": "wrongpassword"}
        )
        
        assert response.status_code == 401
        assert "incorrect" in response.json()["detail"].lower()
    
    def test_login_nonexistent_user(self, client: TestClient):
        """Test login with nonexistent user"""
        response = client.post(
            "/api/auth/login",
            data={"username": "nonexistent@example.com", "password": "password"}
        )
        
        assert response.status_code == 401
        assert "incorrect" in response.json()["detail"].lower()
    
    def test_get_current_user(self, client: TestClient, auth_headers):
        """Test getting current user info"""
        response = client.get("/api/auth/me", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "email" in data
        assert "id" in data
        assert "created_at" in data
    
    def test_get_current_user_unauthorized(self, client: TestClient):
        """Test getting current user without authentication"""
        response = client.get("/api/auth/me")
        
        assert response.status_code == 401
    
    def test_get_current_user_invalid_token(self, client: TestClient):
        """Test getting current user with invalid token"""
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": "Bearer invalid_token"}
        )
        
        assert response.status_code == 401
