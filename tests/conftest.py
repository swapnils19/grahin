"""
Pytest configuration and fixtures for Grahin RAG Application
"""
import pytest
import tempfile
import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.core.database import get_db, Base
from app.core.security import get_password_hash
from app.models import User, File, DocumentChunk, Conversation, Message

# Test database URL (SQLite in memory)
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="session")
def db():
    """Create test database tables"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session(db):
    """Create a fresh database session for each test"""
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(db):
    """Create a test client"""
    return TestClient(app)


@pytest.fixture
def test_user(db_session):
    """Create a test user"""
    user = User(
        email="test@example.com",
        password_hash=get_password_hash("testpassword"),
        full_name="Test User"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_file(db_session, test_user):
    """Create a test file"""
    file = File(
        user_id=test_user.id,
        filename="test_file.pdf",
        original_filename="original.pdf",
        file_type="pdf",
        file_size=1024,
        file_path="/uploads/test_file.pdf",
        mime_type="application/pdf",
        is_processed=True,
        processing_status="completed"
    )
    db_session.add(file)
    db_session.commit()
    db_session.refresh(file)
    return file


@pytest.fixture
def test_chunk(db_session, test_file):
    """Create a test document chunk"""
    chunk = DocumentChunk(
        file_id=test_file.id,
        chunk_index=0,
        content="This is a test document chunk about artificial intelligence and machine learning.",
        embedding_id=f"{test_file.id}_0"
    )
    db_session.add(chunk)
    db_session.commit()
    db_session.refresh(chunk)
    return chunk


@pytest.fixture
def test_conversation(db_session, test_user):
    """Create a test conversation"""
    conversation = Conversation(
        user_id=test_user.id,
        title="Test Conversation"
    )
    db_session.add(conversation)
    db_session.commit()
    db_session.refresh(conversation)
    return conversation


@pytest.fixture
def auth_headers(client, test_user):
    """Get authentication headers for test user"""
    # Login to get token
    response = client.post(
        "/api/auth/login",
        data={"username": test_user.email, "password": "testpassword"}
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def temp_upload_dir():
    """Create a temporary upload directory"""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture
def sample_text_file(temp_upload_dir):
    """Create a sample text file for testing"""
    file_path = os.path.join(temp_upload_dir, "test.txt")
    with open(file_path, "w") as f:
        f.write("This is a test document for the Grahin RAG application. It contains information about artificial intelligence, machine learning, and natural language processing.")
    return file_path
