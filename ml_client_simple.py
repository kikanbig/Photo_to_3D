"""
Простой клиент для RunPod интеграции в Railway
"""
import os
import json
import base64
import asyncio
import httpx
from typing import Dict, Any, Optional

class RunPodClient:
    def __init__(self):
        self.endpoint_id = os.getenv("RUNPOD_ENDPOINT_ID")
        self.api_key = os.getenv("RUNPOD_API_KEY")
        self.enabled = os.getenv("RUNPOD_ENABLED", "false").lower() == "true"
        
        if self.enabled and (not self.endpoint_id or not self.api_key):
            raise ValueError("RUNPOD_ENDPOINT_ID и RUNPOD_API_KEY обязательны когда RUNPOD_ENABLED=true")
    
    async def generate_3d(self, image_data: bytes, task_id: str = "unknown") -> Dict[str, Any]:
        """
        Генерация 3D модели через RunPod
        """
        if not self.enabled:
            return {
                "status": "failed",
                "error": "RunPod не включен",
                "task_id": task_id
            }
        
        try:
            # Кодируем изображение в base64
            image_b64 = base64.b64encode(image_data).decode('utf-8')
            
            # Payload для RunPod
            payload = {
                "input": {
                    "image_data": image_b64,
                    "image_format": "png",
                    "task_id": task_id
                }
            }
            
            # Headers
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # URL для запроса
            url = f"https://api.runpod.ai/v2/{self.endpoint_id}/run"
            
            async with httpx.AsyncClient(timeout=300.0) as client:
                # Отправляем задачу
                response = await client.post(url, json=payload, headers=headers)
                response.raise_for_status()
                result = response.json()
                
                if result.get("status") == "IN_QUEUE":
                    # Ждем выполнения
                    job_id = result["id"]
                    return await self._wait_for_completion(job_id, task_id)
                
                return result
                
        except Exception as e:
            return {
                "status": "failed",
                "error": f"RunPod error: {str(e)}",
                "task_id": task_id
            }
    
    async def _wait_for_completion(self, job_id: str, task_id: str, max_wait: int = 300) -> Dict[str, Any]:
        """
        Ждем завершения задачи в RunPod
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
        }
        
        status_url = f"https://api.runpod.ai/v2/{self.endpoint_id}/status/{job_id}"
        
        async with httpx.AsyncClient() as client:
            for _ in range(max_wait):
                try:
                    response = await client.get(status_url, headers=headers)
                    response.raise_for_status()
                    result = response.json()
                    
                    status = result.get("status", "unknown")
                    
                    if status == "COMPLETED":
                        output = result.get("output", {})
                        return {
                            "status": "completed",
                            "task_id": task_id,
                            "job_id": job_id,
                            "result": output.get("result", {}),
                            "execution_time": result.get("executionTime", 0)
                        }
                    elif status == "FAILED":
                        return {
                            "status": "failed",
                            "error": result.get("error", "RunPod task failed"),
                            "task_id": task_id,
                            "job_id": job_id
                        }
                    
                    await asyncio.sleep(1)
                    
                except Exception as e:
                    return {
                        "status": "failed",
                        "error": f"Status check error: {str(e)}",
                        "task_id": task_id
                    }
        
        return {
            "status": "failed",
            "error": "Timeout waiting for completion",
            "task_id": task_id
        }
