"""
Клиент для подключения к RunPod ML серверу
"""
import os
import httpx
import asyncio
from typing import Dict, Any, Optional
import base64
import json

class RunPodClient:
    def __init__(self, endpoint_id: str, api_key: str):
        self.endpoint_id = endpoint_id
        self.api_key = api_key
        self.base_url = f"https://api.runpod.ai/v2/{endpoint_id}"
        
    async def generate_3d(self, image_data: bytes, image_format: str = "png") -> Dict[str, Any]:
        """
        Отправляет изображение на генерацию 3D модели
        """
        # Кодируем изображение в base64
        image_b64 = base64.b64encode(image_data).decode('utf-8')
        
        payload = {
            "input": {
                "image_data": image_b64,
                "image_format": image_format,
                "output_format": "glb",
                "quality": "medium"
            }
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        async with httpx.AsyncClient(timeout=300.0) as client:
            # Отправляем задачу
            response = await client.post(
                f"{self.base_url}/run",
                json=payload,
                headers=headers
            )
            response.raise_for_status()
            result = response.json()
            
            if result["status"] == "IN_QUEUE" or result["status"] == "IN_PROGRESS":
                # Ждем выполнения
                job_id = result["id"]
                return await self._wait_for_completion(job_id)
            
            return result
    
    async def _wait_for_completion(self, job_id: str, max_wait: int = 300) -> Dict[str, Any]:
        """
        Ждет завершения задачи
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
        }
        
        async with httpx.AsyncClient() as client:
            for _ in range(max_wait):
                response = await client.get(
                    f"{self.base_url}/status/{job_id}",
                    headers=headers
                )
                response.raise_for_status()
                result = response.json()
                
                if result["status"] == "COMPLETED":
                    return result
                elif result["status"] == "FAILED":
                    raise Exception(f"Генерация не удалась: {result.get('error', 'Неизвестная ошибка')}")
                
                await asyncio.sleep(1)
        
        raise TimeoutError("Превышено время ожидания генерации")

# Пример использования
async def test_runpod_client():
    """
    Тестовая функция для проверки клиента
    """
    # Эти значения нужно будет получить из RunPod после деплоя
    ENDPOINT_ID = os.getenv("RUNPOD_ENDPOINT_ID", "your-endpoint-id")
    API_KEY = os.getenv("RUNPOD_API_KEY", "your-api-key")
    
    if ENDPOINT_ID == "your-endpoint-id":
        print("❌ Нужно указать RUNPOD_ENDPOINT_ID и RUNPOD_API_KEY")
        return
    
    client = RunPodClient(ENDPOINT_ID, API_KEY)
    
    # Читаем тестовое изображение
    try:
        with open("test_image.jpg", "rb") as f:
            image_data = f.read()
        
        print("🚀 Отправляем изображение на генерацию...")
        result = await client.generate_3d(image_data, "jpg")
        
        if result["status"] == "COMPLETED":
            output = result["output"]
            print(f"✅ Генерация завершена!")
            print(f"📁 GLB файл: {output.get('glb_url', 'не найден')}")
            print(f"🖼️ Preview: {output.get('preview_url', 'не найден')}")
        else:
            print(f"❌ Ошибка: {result}")
            
    except FileNotFoundError:
        print("❌ Файл test_image.jpg не найден")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    asyncio.run(test_runpod_client())
