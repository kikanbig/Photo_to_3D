#!/usr/bin/env python3
"""
Startup script for Railway deployment
"""
import os
import uvicorn

if __name__ == "__main__":
    # Get port from environment variable, default to 8000
    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "0.0.0.0")
    
    print(f"🚀 Starting server on {host}:{port}")
    print(f"📍 Health check available at: http://{host}:{port}/health")
    
    # Run the server
    uvicorn.run(
        "asgi_app:app",
        host=host,
        port=port,
        workers=1,
        log_level="info"
    )
