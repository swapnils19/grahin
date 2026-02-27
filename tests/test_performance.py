"""
Performance tests for Grahin RAG Application
"""
import pytest
import time
import tempfile
import os
from fastapi.testclient import TestClient


class TestPerformance:
    """Performance and load tests"""

    def test_file_upload_performance(self, client: TestClient, auth_headers, temp_upload_dir):
        """Test file upload performance"""
        # Create a larger test file (1MB)
        test_content = "Test content for performance testing. " * 10000  # ~500KB

        test_file = os.path.join(temp_upload_dir, "large_test.txt")
        with open(test_file, "w") as f:
            f.write(test_content)

        start_time = time.time()

        with open(test_file, "rb") as f:
            response = client.post(
                "/api/files/upload",
                headers=auth_headers,
                files={"file": ("large_test.txt", f, "text/plain")}
            )

        end_time = time.time()
        upload_time = end_time - start_time

        assert response.status_code == 200
        assert upload_time < 10.0  # Should upload within 10 seconds

        print(f"File upload time: {upload_time:.2f} seconds")

    def test_chat_response_performance(self, client: TestClient, auth_headers, test_chunk):
        """Test chat response performance"""
        start_time = time.time()

        response = client.post(
            "/api/chat/chat",
            headers=auth_headers,
            json={
                "message": "What can you tell me about artificial intelligence?",
                "related_files": [str(test_chunk.file_id)]
            }
        )

        end_time = time.time()
        response_time = end_time - start_time

        assert response.status_code == 200
        assert response_time < 30.0  # Should respond within 30 seconds

        print(f"Chat response time: {response_time:.2f} seconds")

    def test_search_performance(self, client: TestClient, auth_headers, test_chunk):
        """Test search performance"""
        start_time = time.time()

        response = client.get(
            "/api/chat/search",
            headers=auth_headers,
            params={"query": "artificial intelligence", "k": 10}
        )

        end_time = time.time()
        search_time = end_time - start_time

        assert response.status_code == 200
        assert search_time < 5.0  # Should search within 5 seconds

        print(f"Search time: {search_time:.2f} seconds")

    def test_concurrent_requests(self, client: TestClient, auth_headers):
        """Test handling multiple concurrent requests"""
        import threading
        import queue

        results = queue.Queue()

        def make_request():
            try:
                response = client.get("/api/files/", headers=auth_headers)
                results.put(response.status_code)
            except Exception as e:
                results.put(f"Error: {e}")

        # Start 10 concurrent requests
        threads = []
        start_time = time.time()

        for _ in range(10):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        end_time = time.time()
        total_time = end_time - start_time

        # Check results
        success_count = 0
        while not results.empty():
            result = results.get()
            if result == 200:
                success_count += 1

        assert success_count >= 8  # At least 80% success rate
        assert total_time < 5.0   # Should complete within 5 seconds

        print(f"Concurrent requests: {success_count}/10 successful in {total_time:.2f} seconds")

    def test_database_query_performance(self, db_session, test_user):
        """Test database query performance"""
        from app.models import File, DocumentChunk

        # Create multiple files and chunks for testing
        files = []
        for i in range(50):
            file = File(
                user_id=test_user.id,
                filename=f"test_file_{i}.pdf",
                original_filename=f"original_{i}.pdf",
                file_type="pdf",
                file_size=1024 * (i + 1),
                file_path=f"/uploads/test_{i}.pdf"
            )
            db_session.add(file)
            files.append(file)

        db_session.commit()

        # Create chunks for each file
        for file in files:
            for j in range(10):
                chunk = DocumentChunk(
                    file_id=file.id,
                    chunk_index=j,
                    content=f"Test chunk content {j} for file {file.filename}",
                    embedding_id=f"{file.id}_{j}"
                )
                db_session.add(chunk)

        db_session.commit()

        # Test query performance
        start_time = time.time()

        # Complex query with joins
        results = db_session.query(File).join(DocumentChunk).filter(
            File.user_id == test_user.id
        ).all()

        end_time = time.time()
        query_time = end_time - start_time

        assert len(results) == 50
        assert query_time < 1.0  # Should complete within 1 second

        print(f"Database query time: {query_time:.3f} seconds for {len(results)} results")

    def test_memory_usage(self, client: TestClient, auth_headers, test_user):
        """Test memory usage doesn't grow excessively"""
        import psutil
        import os

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Make multiple requests
        for i in range(20):
            response = client.get("/api/files/", headers=auth_headers)
            assert response.status_code == 200

        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_growth = final_memory - initial_memory

        # Memory growth should be reasonable (less than 50MB)
        assert memory_growth < 50.0

        print(f"Memory usage: {initial_memory:.1f}MB → {final_memory:.1f}MB (growth: {memory_growth:.1f}MB)")

    def test_large_conversation_history(self, client: TestClient, auth_headers, test_conversation):
        """Test performance with large conversation history"""
        from app.core.database import SessionLocal
        from app.models import Message

        db_session = SessionLocal()

        try:
            # Add many messages to conversation
            for i in range(100):
                message = Message(
                    conversation_id=test_conversation.id,
                    role="user" if i % 2 == 0 else "assistant",
                    content=f"Message {i+1}: " + "x" * 100  # 100 character messages
                )
                db_session.add(message)

            db_session.commit()

            # Test retrieving conversation
            start_time = time.time()

            response = client.get(
                f"/api/chat/conversations/{test_conversation.id}",
                headers=auth_headers
            )

            end_time = time.time()
            response_time = end_time - start_time

            assert response.status_code == 200
            assert response_time < 2.0  # Should retrieve within 2 seconds

            data = response.json()
            assert len(data["messages"]) >= 100

            print(f"Large conversation retrieval: {response_time:.2f} seconds for {len(data['messages'])} messages")
        finally:
            db_session.close()
