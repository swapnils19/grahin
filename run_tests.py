#!/usr/bin/env python3
"""
Comprehensive test runner for Grahin RAG Application
"""
import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, description):
    """Run a command and return success status"""
    print(f"\n🧪 {description}")
    print("=" * 50)
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=Path(__file__).parent)
        
        if result.stdout:
            print(result.stdout)
        
        if result.stderr:
            print(f"Errors: {result.stderr}")
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Error running {description}: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Grahin RAG Application - Test Suite")
    print("=" * 60)
    
    tests = [
        ("poetry run python test_sqlalchemy.py", "SQLAlchemy + Pydantic Integration"),
        ("poetry run python test_api.py", "API Endpoints Test"),
        ("poetry run pytest tests/ -v", "Pytest Unit Tests"),
        ("poetry run pytest tests/test_auth.py -v", "Authentication Tests"),
        ("poetry run pytest tests/test_files.py -v", "File Management Tests"),
        ("poetry run pytest tests/test_chat.py -v", "Chat & RAG Tests"),
        ("poetry run pytest tests/test_models.py -v", "Database Model Tests"),
        ("poetry run pytest tests/test_integration.py -v", "Integration Tests"),
        ("poetry run pytest tests/test_performance.py -v -s", "Performance Tests"),
    ]
    
    results = []
    
    for cmd, description in tests:
        success = run_command(cmd, description)
        results.append((description, success))
        
        if not success:
            print(f"⚠️  {description} failed!")
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for description, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {description}")
        if success:
            passed += 1
        else:
            failed += 1
    
    print(f"\n🎯 Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! Your RAG application is ready!")
        return 0
    else:
        print("💥 Some tests failed. Please check the implementation.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
