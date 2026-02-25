#!/usr/bin/env python3
"""
PDB Debugging Guide for RAG Application
Run this script to see different pdb debugging techniques in action
"""

import pdb
import uuid
from app.services.rag_service import RAGService

def debug_rag_service():
    """Debug RAGService initialization and methods"""
    print("=== Debugging RAGService ===")
    
    # Method 1: Simple breakpoint
    pdb.set_trace()
    
    rag_service = RAGService()
    
    # Method 2: Conditional breakpoint
    user_id = uuid.uuid4()
    if user_id:
        pdb.set_trace()  # Only breaks if user_id exists
    
    # Method 3: Break with context
    print(f"Debugging with user_id: {user_id}")
    pdb.set_trace()
    
    vector_store = rag_service.get_user_vector_store(user_id)
    print(f"Vector store created: {vector_store}")

def debug_with_pdb_commands():
    """Show useful pdb commands"""
    print("=== PDB Commands Demo ===")
    
    # Set a breakpoint and run this function
    pdb.set_trace()
    
    test_data = {
        "user_id": uuid.uuid4(),
        "query": "test query",
        "file_ids": [uuid.uuid4()]
    }
    
    # In pdb, try these commands:
    # l (list) - Show current code
    # n (next) - Execute next line
    # s (step) - Step into function
    # c (continue) - Continue execution
    # p variable (print) - Print variable value
    # pp variable - Pretty print variable
    # w (where) - Show stack trace
    # q (quit) - Quit debugger
    
    print("Data ready for inspection")

def debug_exception_handling():
    """Debug exception handling in RAG operations"""
    print("=== Exception Debugging ===")
    
    try:
        # This will likely cause an error
        rag_service = RAGService()
        pdb.set_trace()
        
        # Try to search with invalid user_id
        results = rag_service.search_documents(
            user_id=uuid.uuid4(),  # Non-existent user
            query="test query"
        )
        
    except Exception as e:
        print(f"Exception caught: {e}")
        # Debug the exception
        pdb.set_trace()
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("PDB Debugging Examples")
    print("Run this script and use pdb commands to debug")
    
    # Uncomment the function you want to test:
    # debug_rag_service()
    # debug_with_pdb_commands()
    debug_exception_handling()
