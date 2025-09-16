"""
Упрощенное ASGI приложение с RunPod интеграцией
"""
import json
import uuid
import os
import base64
import asyncio
from datetime import datetime
from typing import Dict, Any

try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False

# RunPod configuration
RUNPOD_ENDPOINT_ID = os.getenv("RUNPOD_ENDPOINT_ID")
RUNPOD_API_KEY = os.getenv("RUNPOD_API_KEY") 
RUNPOD_ENABLED = os.getenv("RUNPOD_ENABLED", "false").lower() == "true"

async def call_runpod(image_data: bytes, task_id: str) -> Dict[str, Any]:
    """Вызов RunPod для генерации 3D модели"""
    if not RUNPOD_ENABLED or not HTTPX_AVAILABLE:
        return {
            "status": "failed",
            "error": "RunPod не настроен или httpx недоступен"
        }
    
    try:
        image_b64 = base64.b64encode(image_data).decode('utf-8')
        
        payload = {
            "input": {
                "image_data": image_b64,
                "image_format": "jpg",
                "task_id": task_id
            }
        }
        
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
                job_id = result["id"]
                return await wait_runpod_completion(job_id, task_id)
            
            return result
            
    except Exception as e:
        return {
            "status": "failed",
            "error": f"RunPod error: {str(e)}"
        }

async def wait_runpod_completion(job_id: str, task_id: str) -> Dict[str, Any]:
    """Ждем завершения задачи в RunPod"""
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
                        "result": result.get("output", {}),
                        "execution_time": result.get("executionTime", 0)
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

async def parse_multipart_data(receive):
    """Упрощенный парсер multipart/form-data для изображений"""
    body = b""
    
    # Читаем все данные
    while True:
        message = await receive()
        if message["type"] == "http.request":
            body += message.get("body", b"")
            if not message.get("more_body", False):
                break
    
    # Ищем изображение в multipart данных
    if b"image" in body and (b"jpeg" in body or b"jpg" in body or b"png" in body):
        # Упрощенное извлечение изображения
        parts = body.split(b"\r\n\r\n")
        for i, part in enumerate(parts):
            if b"\xff\xd8\xff" in part:  # JPEG magic bytes
                # Находим начало JPEG
                start = part.find(b"\xff\xd8\xff")
                # Ищем конец в следующих частях
                image_data = part[start:]
                for j in range(i + 1, len(parts)):
                    if b"------" in parts[j]:  # Граница multipart
                        boundary_pos = parts[j].find(b"------")
                        image_data += b"\r\n\r\n" + parts[j][:boundary_pos]
                        break
                    else:
                        image_data += b"\r\n\r\n" + parts[j]
                
                # Убираем лишние данные в конце
                if b"------" in image_data:
                    boundary_pos = image_data.rfind(b"------")
                    image_data = image_data[:boundary_pos-4]  # -4 для \r\n\r\n
                
                return image_data
    
    return None

async def app(scope: Dict[str, Any], receive, send):
    """ASGI приложение"""
    
    if scope["type"] == "http":
        path = scope["path"]
        method = scope["method"]
        
        # Health check
        if path == "/health" and method == "GET":
            response = {
                "status": "healthy",
                "version": "1.0.0",
                "runpod_enabled": RUNPOD_ENABLED,
                "httpx_available": HTTPX_AVAILABLE
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
        
        # Generate 3D model
        if path == "/api/v1/generate" and method == "POST":
            try:
                # Парсим изображение из multipart данных
                image_data = await parse_multipart_data(receive)
                
                if not image_data:
                    response = {
                        "error": "No image found in request"
                    }
                    status_code = 400
                else:
                    # Генерируем task_id
                    task_id = str(uuid.uuid4())
                    
                    if RUNPOD_ENABLED and HTTPX_AVAILABLE:
                        # Вызываем RunPod
                        result = await call_runpod(image_data, task_id)
                        
                        if result.get("status") == "completed":
                            response = {
                                "task_id": task_id,
                                "status": "completed",
                                "message": "3D model generated successfully",
                                "job_id": result.get("job_id"),
                                "execution_time": result.get("execution_time"),
                                "result": result.get("result", {})
                            }
                            status_code = 200
                        else:
                            response = {
                                "task_id": task_id,
                                "status": "failed",
                                "error": result.get("error", "Generation failed"),
                                "job_id": result.get("job_id")
                            }
                            status_code = 500
                    else:
                        # Demo режим
                        response = {
                            "task_id": task_id,
                            "status": "demo",
                            "message": "RunPod не настроен - демо режим",
                            "image_size": len(image_data)
                        }
                        status_code = 200
                
            except Exception as e:
                response = {
                    "error": f"Generation failed: {str(e)}"
                }
                status_code = 500
            
            body = json.dumps(response).encode()
            
            await send({
                "type": "http.response.start",
                "status": status_code,
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
        
        # 404 для всех остальных путей
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
        return
