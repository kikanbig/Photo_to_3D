"""
ASGI приложение с поддержкой базы данных
"""
import json
import uuid
from datetime import datetime
from typing import Dict, Any
from database import SessionLocal, GenerationTask, GenerationStatus, init_database

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
        
        # Generate endpoint - теперь с реальной БД
        if path == "/api/v1/generate" and method == "POST":
            try:
                # Создаем новую задачу в БД
                db = SessionLocal()
                task_id = str(uuid.uuid4())
                created_time = datetime.utcnow()
                
                task = GenerationTask(
                    id=task_id,
                    original_image_url="demo-image.jpg",  # TODO: получать из POST данных
                    status=GenerationStatus.PENDING.value,
                    created_at=created_time
                )
                
                db.add(task)
                db.commit()
                db.close()
                
                response = {
                    "task_id": task_id,
                    "status": "pending",
                    "message": "3D generation task created successfully",
                    "created_at": created_time.isoformat()
                }
                
            except Exception as e:
                response = {
                    "error": "Failed to create generation task",
                    "details": str(e)
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
        
        # Task status endpoint
        if path.startswith("/api/v1/task/") and method == "GET":
            task_id = path.split("/")[-1]
            
            try:
                db = SessionLocal()
                task = db.query(GenerationTask).filter(GenerationTask.id == task_id).first()
                db.close()
                
                if task:
                    response = {
                        "task_id": task.id,
                        "status": task.status,
                        "created_at": task.created_at.isoformat(),
                        "glb_url": task.glb_file_url,
                        "ply_url": task.ply_file_url,
                        "preview_url": task.preview_video_url,
                        "error_message": task.error_message
                    }
                else:
                    response = {"error": "Task not found"}
                    
            except Exception as e:
                response = {
                    "error": "Failed to get task status", 
                    "details": str(e)
                }
            
            body = json.dumps(response).encode()
            
            await send({
                "type": "http.response.start",
                "status": 200 if "error" not in response else 404,
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
        
        # List all tasks endpoint
        if path == "/api/v1/tasks" and method == "GET":
            try:
                db = SessionLocal()
                tasks = db.query(GenerationTask).order_by(GenerationTask.created_at.desc()).limit(10).all()
                db.close()
                
                response = {
                    "tasks": [
                        {
                            "task_id": task.id,
                            "status": task.status,
                            "created_at": task.created_at.isoformat(),
                            "original_filename": task.original_filename
                        }
                        for task in tasks
                    ]
                }
                
            except Exception as e:
                response = {
                    "error": "Failed to get tasks",
                    "details": str(e)
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
