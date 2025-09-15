"""
Простейшее ASGI приложение для Railway без FastAPI
"""
import json
from typing import Dict, Any

async def app(scope: Dict[str, Any], receive, send):
    """ASGI приложение"""
    
    if scope["type"] == "http":
        path = scope["path"]
        method = scope["method"]
        
        # Health check endpoint
        if path == "/health" and method == "GET":
            response = {
                "status": "healthy",
                "version": "1.0.0",
                "mode": "railway_demo"
            }
            body = json.dumps(response).encode()
            
            await send({
                "type": "http.response.start",
                "status": 200,
                "headers": [
                    [b"content-type", b"application/json"],
                    [b"content-length", str(len(body)).encode()],
                ],
            })
            await send({
                "type": "http.response.body",
                "body": body,
            })
            return
        
        # Root endpoint
        if path == "/" and method == "GET":
            response = {"message": "Photo to 3D API is running"}
            body = json.dumps(response).encode()
            
            await send({
                "type": "http.response.start",
                "status": 200,
                "headers": [
                    [b"content-type", b"application/json"],
                    [b"content-length", str(len(body)).encode()],
                ],
            })
            await send({
                "type": "http.response.body",
                "body": body,
            })
            return
        
        # API status endpoint
        if path == "/api/v1/status" and method == "GET":
            response = {
                "api": "v1",
                "status": "operational",
                "endpoints": ["/health", "/api/v1/status", "/api/v1/generate"]
            }
            body = json.dumps(response).encode()
            
            await send({
                "type": "http.response.start",
                "status": 200,
                "headers": [
                    [b"content-type", b"application/json"],
                    [b"content-length", str(len(body)).encode()],
                ],
            })
            await send({
                "type": "http.response.body",
                "body": body,
            })
            return
        
        # Generate endpoint
        if path == "/api/v1/generate" and method == "POST":
            response = {
                "task_id": "demo-task-123",
                "status": "completed",
                "message": "3D model generated successfully (demo mode)",
                "glb_url": "/download/demo-task-123.glb",
                "ply_url": "/download/demo-task-123.ply"
            }
            body = json.dumps(response).encode()
            
            await send({
                "type": "http.response.start",
                "status": 200,
                "headers": [
                    [b"content-type", b"application/json"],
                    [b"content-length", str(len(body)).encode()],
                ],
            })
            await send({
                "type": "http.response.body",
                "body": body,
            })
            return
        
        # 404 for other paths
        response = {"error": "Not found"}
        body = json.dumps(response).encode()
        
        await send({
            "type": "http.response.start",
            "status": 404,
            "headers": [
                [b"content-type", b"application/json"],
                [b"content-length", str(len(body)).encode()],
            ],
        })
        await send({
            "type": "http.response.body",
            "body": body,
        })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("asgi_app:app", host="0.0.0.0", port=8000, reload=True)
