import uuid
import pdb
import os
from typing import List, Optional, Dict, Any
from pathlib import Path

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.chains import RetrievalQA
from langchain_anthropic import ChatAnthropic
from langchain.prompts import PromptTemplate
from langchain.schema import Document

from app.core.config import settings
from app.core.database import SessionLocal
from app.models.file import DocumentChunk, File
from app.models.user import User


class RAGService:
    def __init__(self):
        # Clear proxy environment variables to prevent conflicts
        proxy_vars = ['http_proxy', 'https_proxy', 'HTTP_PROXY', 'HTTPS_PROXY']
        for var in proxy_vars:
            if var in os.environ:
                del os.environ[var]

        # Initialize embeddings
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )

        # Initialize vector store
        self.persist_directory = Path(settings.chroma_persist_dir)
        self.persist_directory.mkdir(exist_ok=True)

        # pdb.set_trace()
        # Initialize Claude LLM
        self.llm = ChatAnthropic(
            model="claude-3-5-sonnet-20241022",
            api_key=settings.claude_api_key
        )

        # Create prompt template
        self.prompt_template = PromptTemplate(
            template="""Use the following pieces of context to answer the question at the end.
            If you don't know the answer from the context, just say that you don't know.
            Do not try to make up an answer. Keep the answer concise and relevant.

            Context: {context}

            Question: {question}

            Answer:""",
            input_variables=["context", "question"]
        )

    def get_user_vector_store(self, user_id: uuid.UUID) -> Chroma:
        """Get or create vector store for a specific user"""
        collection_name = f"user_{user_id}"

        vector_store = Chroma(
            collection_name=collection_name,
            embedding_function=self.embeddings,
            persist_directory=str(self.persist_directory)
        )

        return vector_store

    def add_documents_to_vector_store(self, user_id: uuid.UUID, file_id: uuid.UUID):
        """Add document chunks to user's vector store"""
        db = SessionLocal()
        try:
            # Get document chunks for this file
            chunks = db.query(DocumentChunk).filter(
                DocumentChunk.file_id == file_id
            ).all()

            if not chunks:
                return

            # Create LangChain documents
            documents = []
            for chunk in chunks:
                doc = Document(
                    page_content=chunk.content,
                    metadata={
                        "chunk_id": str(chunk.id),
                        "file_id": str(chunk.file_id),
                        "chunk_index": chunk.chunk_index
                    }
                )
                documents.append(doc)

            # Add to vector store
            vector_store = self.get_user_vector_store(user_id)
            vector_store.add_documents(documents)
            vector_store.persist()

            # Update chunks with embedding IDs
            for i, chunk in enumerate(chunks):
                chunk.embedding_id = f"{chunk.file_id}_{chunk.chunk_index}"

            db.commit()

        finally:
            db.close()

    def search_documents(self, user_id: uuid.UUID, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Search for relevant documents"""
        vector_store = self.get_user_vector_store(user_id)

        # Search for similar documents
        results = vector_store.similarity_search_with_score(query, k=k)

        # Format results
        formatted_results = []
        for doc, score in results:
            formatted_results.append({
                "content": doc.page_content,
                "metadata": doc.metadata,
                "score": score
            })

        return formatted_results

    def generate_response(self, user_id: uuid.UUID, query: str, file_ids: Optional[List[uuid.UUID]] = None) -> str:
        """Generate response using RAG"""
        # Search for relevant documents
        search_results = self.search_documents(user_id, query, k=5)

        # Build context from search results
        context = "\n\n".join([result["content"] for result in search_results])

        # Create prompt with context
        prompt = f"""Use the following pieces of context to answer the question at the end.
If you don't know the answer from the context, just say that you don't know.
Do not try to make up an answer. Keep the answer concise and relevant.

Context: {context}

Question: {query}

Answer:"""

        # Generate response using LangChain ChatAnthropic
        response = self.llm.invoke(prompt)

        return response.content

    def get_user_files_summary(self, user_id: uuid.UUID) -> Dict[str, Any]:
        """Get summary of user's uploaded files"""
        db = SessionLocal()
        try:
            files = db.query(File).filter(
                File.user_id == user_id,
                File.is_processed == True
            ).all()

            total_files = len(files)
            total_chunks = sum(len(file.chunks) for file in files)

            return {
                "total_files": total_files,
                "total_chunks": total_chunks,
                "files": [
                    {
                        "id": str(file.id),
                        "filename": file.original_filename,
                        "file_type": file.file_type,
                        "chunks_count": len(file.chunks)
                    }
                    for file in files
                ]
            }

        finally:
            db.close()

    def delete_file_from_vector_store(self, user_id: uuid.UUID, file_id: uuid.UUID):
        """Remove file documents from vector store"""
        db = SessionLocal()
        try:
            # Get chunks for this file
            chunks = db.query(DocumentChunk).filter(
                DocumentChunk.file_id == file_id
            ).all()

            if not chunks:
                return

            # Get vector store
            vector_store = self.get_user_vector_store(user_id)

            # Delete documents by IDs
            ids_to_delete = [f"{chunk.file_id}_{chunk.chunk_index}" for chunk in chunks]
            vector_store.delete(ids_to_delete)
            vector_store.persist()

        finally:
            db.close()


rag_service = RAGService()
