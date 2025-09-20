"""
Прямой тест с реальным фото через RunPod (без Railway)
"""
import os
import requests
import base64
import json
import time
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

def test_photo_direct():
    """
    Тест генерации 3D модели с реальным фото напрямую через RunPod
    """
    # RunPod credentials
    ENDPOINT_ID = "z34poz9n7a9487"
    API_KEY = os.getenv("RUNPOD_API_KEY", "RP-...")
    
    # Путь к фото
    photo_path = "/Users/kikanbig/Мои стартапы/Photo_to_3D/Фото для моделей/4879854.jpg"
    
    print("🧪 Тестирование генерации 3D модели с реальным фото")
    print("=" * 55)
    print(f"📸 Фото: {os.path.basename(photo_path)}")
    
    # Проверяем фото
    if not os.path.exists(photo_path):
        print(f"❌ Фото не найдено: {photo_path}")
        return
    
    # Загружаем и кодируем фото
    try:
        with open(photo_path, "rb") as f:
            image_data = f.read()
        
        print(f"📁 Размер файла: {len(image_data):,} bytes")
        
        # Кодируем в base64
        image_b64 = base64.b64encode(image_data).decode('utf-8')
        print(f"📋 Base64 длина: {len(image_b64):,} символов")
        
        # Payload для RunPod
        payload = {
            "input": {
                "image_data": image_b64,
                "image_format": "jpg",
                "task_id": f"photo_test_{int(time.time())}",
                "output_format": "glb"
            }
        }
        
        # Headers
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }
        
        # URL
        url = f"https://api.runpod.ai/v2/{ENDPOINT_ID}/run"
        
        print("🚀 Отправляем в RunPod...")
        response = requests.post(url, json=payload, headers=headers, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Запрос принят RunPod!")
            print(f"📋 Job ID: {result.get('id', 'неизвестно')}")
            print(f"📊 Status: {result.get('status', 'неизвестно')}")
            
            if result.get('status') == 'IN_QUEUE':
                job_id = result['id']
                print("⏳ Ждем генерации 3D модели...")
                check_runpod_status(ENDPOINT_ID, job_id, API_KEY)
            
        else:
            print(f"❌ Ошибка RunPod: {response.status_code}")
            print(f"📄 Ответ: {response.text}")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")

def check_runpod_status(endpoint_id: str, job_id: str, api_key: str, max_attempts: int = 120):
    """
    Проверяем статус в RunPod (до 2 минут)
    """
    headers = {"Authorization": f"Bearer {api_key}"}
    status_url = f"https://api.runpod.ai/v2/{endpoint_id}/status/{job_id}"
    
    for attempt in range(max_attempts):
        try:
            response = requests.get(status_url, headers=headers)
            if response.status_code == 200:
                result = response.json()
                status = result.get('status', 'unknown')
                
                print(f"📊 Попытка {attempt + 1}: {status}")
                
                if status == 'COMPLETED':
                    print("🎉 3D модель сгенерирована!")
                    output = result.get('output', {})
                    
                    if 'result' in output:
                        res = output['result']
                        print(f"📁 GLB файл: {res.get('glb_path', 'не найден')}")
                        print(f"📁 PLY файл: {res.get('ply_path', 'не найден')}")
                    
                    print(f"⏱️ Время выполнения: {result.get('executionTime', 0)} секунд")
                    print(f"⏱️ Время ожидания: {result.get('delayTime', 0)} мс")
                    return True
                    
                elif status == 'FAILED':
                    print("❌ Генерация провалилась!")
                    print(f"🔍 Ошибка: {result.get('error', 'неизвестная')}")
                    return False
                
                time.sleep(1)
                
        except Exception as e:
            print(f"❌ Ошибка проверки: {e}")
            time.sleep(2)
    
    print("⏰ Превышено время ожидания")
    return False

if __name__ == "__main__":
    test_photo_direct()
