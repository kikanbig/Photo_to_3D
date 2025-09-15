#!/usr/bin/env python3
"""
Startup script for Railway deployment with database
"""
import os
import uvicorn
from database import init_database

if __name__ == "__main__":
    # Get port from environment variable, default to 8000
    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "0.0.0.0")
    
    print(f"🚀 Starting Photo to 3D server on {host}:{port}")
    print(f"📍 Health check available at: http://{host}:{port}/health")
    
    # Initialize database
    try:
        print("📊 Initializing database...")
        init_database()
        print("✅ Database ready!")
    except Exception as e:
        print(f"⚠️ Database initialization failed: {e}")
        print("🔄 Continuing without database (fallback mode)")
    
    # Run the server
    uvicorn.run(
        "asgi_app:app",
        host=host,
        port=port,
        workers=1,
        log_level="info"
    )
