"""
Полный тест интеграции Railway + RunPod с реальным фото
"""
import os
import requests
import base64
import json
import time
from pathlib import Path

def test_full_integration():
    """
    Тестируем полную цепочку: фото → Railway API → RunPod → 3D модель
    """
    
    # Путь к тестовому фото
    photo_path = "/Users/kikanbig/Мои стартапы/Photo_to_3D/Фото для моделей/4879854.jpg"
    
    # URL Railway API
    railway_urls = [
        "https://web-production-24c39.up.railway.app",
        "https://web-production-4d26.up.railway.app",
        "https://photo-to-3d-production.up.railway.app"
    ]
    
    print("🧪 Тестирование полной интеграции Photo to 3D")
    print("=" * 50)
    
    # Проверяем что фото существует
    if not os.path.exists(photo_path):
        print(f"❌ Фото не найдено: {photo_path}")
        return
    
    print(f"📸 Используем фото: {os.path.basename(photo_path)}")
    
    # Находим рабочий URL Railway
    railway_url = None
    for url in railway_urls:
        try:
            response = requests.get(f"{url}/health", timeout=10)
            if response.status_code == 200:
                railway_url = url
                print(f"✅ Railway найден: {url}")
                break
        except:
            continue
    
    if not railway_url:
        print("❌ Railway API недоступен")
        print("Попробуй найти правильный URL в Railway Dashboard")
        return
    
    # Загружаем и кодируем фото
    try:
        with open(photo_path, "rb") as f:
            image_data = f.read()
        
        print(f"📁 Размер фото: {len(image_data)} bytes")
        
        # Отправляем на генерацию через Railway API
        print("🚀 Отправляем запрос в Railway API...")
        
        files = {
            'image': ('photo.jpg', image_data, 'image/jpeg')
        }
        
        response = requests.post(
            f"{railway_url}/api/v1/generate",
            files=files,
            timeout=300  # 5 минут максимум
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Запрос принят Railway!")
            print(f"📋 Task ID: {result.get('task_id', 'неизвестно')}")
            print(f"📊 Status: {result.get('status', 'неизвестно')}")
            
            # Если есть task_id, проверяем статус
            task_id = result.get('task_id')
            if task_id:
                print("⏳ Ждем завершения генерации...")
                check_task_status(railway_url, task_id)
            
        else:
            print(f"❌ Ошибка Railway API: {response.status_code}")
            print(f"📄 Ответ: {response.text}")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")

def check_task_status(railway_url: str, task_id: str, max_attempts: int = 60):
    """
    Проверяем статус задачи в Railway
    """
    for attempt in range(max_attempts):
        try:
            response = requests.get(f"{railway_url}/api/v1/task/{task_id}")
            if response.status_code == 200:
                result = response.json()
                status = result.get('status', 'unknown')
                
                print(f"📊 Попытка {attempt + 1}: {status}")
                
                if status == 'completed':
                    print("🎉 Генерация завершена!")
                    print(f"📁 GLB URL: {result.get('output_glb_url', 'не найден')}")
                    print(f"⏱️ Время: {result.get('created_at', 'неизвестно')} → {result.get('completed_at', 'неизвестно')}")
                    return True
                elif status == 'failed':
                    print("❌ Генерация провалилась!")
                    print(f"🔍 Ошибка: {result.get('error_message', 'неизвестная')}")
                    return False
                elif status in ['pending', 'processing']:
                    time.sleep(5)  # Ждем 5 секунд
                    continue
                else:
                    print(f"⚠️ Неизвестный статус: {status}")
                    time.sleep(5)
                    
        except Exception as e:
            print(f"❌ Ошибка проверки статуса: {e}")
            time.sleep(5)
    
    print("⏰ Превышено время ожидания")
    return False

if __name__ == "__main__":
    test_full_integration()
