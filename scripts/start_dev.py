#!/usr/bin/env python3
"""
Development server startup script
"""
import os
import sys
import uvicorn

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
