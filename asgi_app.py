"""
ASGI приложение с поддержкой базы данных и RunPod интеграции
"""
import json
import uuid
import os
import base64
import asyncio
from datetime import datetime
from typing import Dict, Any
from database import SessionLocal, GenerationTask, GenerationStatus, init_database

try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False
    print("⚠️ httpx не установлен - RunPod интеграция недоступна")

# RunPod configuration
RUNPOD_ENDPOINT_ID = os.getenv("RUNPOD_ENDPOINT_ID")
RUNPOD_API_KEY = os.getenv("RUNPOD_API_KEY") 
RUNPOD_ENABLED = os.getenv("RUNPOD_ENABLED", "false").lower() == "true"

async def call_runpod(image_data: bytes, task_id: str) -> Dict[str, Any]:
    """
    Вызов RunPod для генерации 3D модели
    """
    if not RUNPOD_ENABLED or not HTTPX_AVAILABLE:
        return {
            "status": "failed",
            "error": "RunPod не настроен или httpx недоступен"
        }
    
    try:
        # Кодируем изображение
        image_b64 = base64.b64encode(image_data).decode('utf-8')
        
        # Payload
        payload = {
            "input": {
                "image_data": image_b64,
                "image_format": "jpg",
                "task_id": task_id
            }
        }
        
        # Headers
        headers = {
            "Authorization": f"Bearer {RUNPOD_API_KEY}",
            "Content-Type": "application/json"
        }
        
        url = f"https://api.runpod.ai/v2/{RUNPOD_ENDPOINT_ID}/run"
        
        async with httpx.AsyncClient(timeout=300.0) as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            result = response.json()
            
            if result.get("status") == "IN_QUEUE":
                # Ждем выполнения
                job_id = result["id"]
                return await wait_runpod_completion(job_id, task_id)
            
            return result
            
    except Exception as e:
        return {
            "status": "failed",
            "error": f"RunPod error: {str(e)}"
        }

async def wait_runpod_completion(job_id: str, task_id: str) -> Dict[str, Any]:
    """
    Ждем завершения задачи в RunPod
    """
    headers = {"Authorization": f"Bearer {RUNPOD_API_KEY}"}
    status_url = f"https://api.runpod.ai/v2/{RUNPOD_ENDPOINT_ID}/status/{job_id}"
    
    async with httpx.AsyncClient() as client:
        for _ in range(300):  # 5 минут максимум
            try:
                response = await client.get(status_url, headers=headers)
                response.raise_for_status()
                result = response.json()
                
                status = result.get("status", "unknown")
                
                if status == "COMPLETED":
                    return {
                        "status": "completed",
                        "job_id": job_id,
                        "result": result.get("output", {})
                    }
                elif status == "FAILED":
                    return {
                        "status": "failed",
                        "error": result.get("error", "RunPod task failed"),
                        "job_id": job_id
                    }
                
                await asyncio.sleep(1)
                
            except Exception as e:
                return {
                    "status": "failed",
                    "error": f"Status check error: {str(e)}"
                }
    
    return {
        "status": "failed",
        "error": "Timeout waiting for completion"
    }

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
