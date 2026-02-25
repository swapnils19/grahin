#!/usr/bin/env python3
"""
Simple API test script for Grahin RAG Application
Run this after starting the development server to test basic functionality
"""

import requests
import json
import time

# Configuration
BASE_URL = "http://localhost:8000"
TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "password123"

def test_health():
    """Test health endpoint"""
    print("🔍 Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure it's running on localhost:8000")
        return False

def register_user():
    """Test user registration"""
    print("\n👤 Testing user registration...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/register",
            json={
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD,
                "full_name": "Test User"
            }
        )
        if response.status_code == 200:
            print("✅ User registration successful")
            return True
        elif response.status_code == 400 and "already registered" in response.text:
            print("ℹ️  User already exists (expected)")
            return True
        else:
            print(f"❌ Registration failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Registration error: {e}")
        return False

def login_user():
    """Test user login and get token"""
    print("\n🔐 Testing user login...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            data={
                "username": TEST_EMAIL,
                "password": TEST_PASSWORD
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        if response.status_code == 200:
            token_data = response.json()
            token = token_data["access_token"]
            print("✅ Login successful")
            return token
        else:
            print(f"❌ Login failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Login error: {e}")
        return None

def test_user_info(token):
    """Test getting user info"""
    print("\n👤 Testing user info endpoint...")
    try:
        response = requests.get(
            f"{BASE_URL}/api/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        if response.status_code == 200:
            user_data = response.json()
            print(f"✅ User info retrieved: {user_data['email']}")
            return True
        else:
            print(f"❌ Failed to get user info: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ User info error: {e}")
        return False

def test_file_upload(token):
    """Test file upload (creates a dummy file)"""
    print("\n📁 Testing file upload...")
    try:
        # Create a simple test file
        test_content = "This is a test document for the Grahin RAG application. It contains some sample text to test the file upload and processing functionality."
        
        files = {'file': ('test.txt', test_content, 'text/plain')}
        response = requests.post(
            f"{BASE_URL}/api/files/upload",
            files=files,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        if response.status_code == 200:
            file_data = response.json()
            print(f"✅ File uploaded successfully: {file_data['original_filename']}")
            return file_data['id']
        else:
            print(f"❌ File upload failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ File upload error: {e}")
        return None

def test_list_files(token):
    """Test listing files"""
    print("\n📋 Testing file listing...")
    try:
        response = requests.get(
            f"{BASE_URL}/api/files/",
            headers={"Authorization": f"Bearer {token}"}
        )
        if response.status_code == 200:
            files_data = response.json()
            print(f"✅ Files listed: {files_data['total']} files found")
            return True
        else:
            print(f"❌ Failed to list files: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ File listing error: {e}")
        return False

def test_chat(token, file_id=None):
    """Test chat functionality"""
    print("\n💬 Testing chat functionality...")
    try:
        message = "What can you tell me about the documents I've uploaded?"
        data = {
            "message": message
        }
        if file_id:
            data["related_files"] = [file_id]
        
        response = requests.post(
            f"{BASE_URL}/api/chat/chat",
            json=data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        if response.status_code == 200:
            chat_response = response.json()
            print(f"✅ Chat response received: {chat_response['message'][:100]}...")
            return True
        else:
            print(f"❌ Chat failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Chat error: {e}")
        return False

def test_search(token):
    """Test search functionality"""
    print("\n🔍 Testing search functionality...")
    try:
        response = requests.get(
            f"{BASE_URL}/api/chat/search",
            params={"query": "test document", "k": 3},
            headers={"Authorization": f"Bearer {token}"}
        )
        
        if response.status_code == 200:
            search_results = response.json()
            print(f"✅ Search completed: {len(search_results['results'])} results found")
            return True
        else:
            print(f"❌ Search failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Search error: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Grahin RAG Application - API Test Suite")
    print("=" * 50)
    
    # Test health first
    if not test_health():
        return
    
    # Test authentication
    if not register_user():
        return
    
    token = login_user()
    if not token:
        return
    
    if not test_user_info(token):
        return
    
    # Test file operations
    file_id = test_file_upload(token)
    test_list_files(token)
    
    # Wait a bit for file processing
    print("\n⏳ Waiting for file processing...")
    time.sleep(2)
    
    # Test chat and search
    test_chat(token, file_id)
    test_search(token)
    
    print("\n🎉 API testing completed!")
    print("\n💡 You can now:")
    print("- Visit http://localhost:8000/docs for interactive API documentation")
    print("- Use the token for manual API testing")
    print("- Upload real documents and test the RAG functionality")

if __name__ == "__main__":
    main()
