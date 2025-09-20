#!/usr/bin/env python3
"""
Тест исправленного RunPod worker'а с PyTorch совместимостью
"""
import os
import json
import base64
import time
import requests
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

RUNPOD_API_KEY = os.getenv("RUNPOD_API_KEY")
RUNPOD_ENDPOINT_ID = os.getenv("RUNPOD_ENDPOINT_ID", "z34poz9n7a9487")

if not RUNPOD_API_KEY:
    print("❌ RUNPOD_API_KEY не найден в .env файле")
    exit(1)

def create_test_image():
    """Создаем простое тестовое изображение"""
    from PIL import Image, ImageDraw
    import io
    
    # Создаем простое изображение 512x512
    img = Image.new('RGB', (512, 512), color='white')
    draw = ImageDraw.Draw(img)
    
    # Рисуем простой объект (круг)
    draw.ellipse([156, 156, 356, 356], fill='red', outline='black', width=3)
    draw.text((200, 400), "Test Object", fill='black')
    
    # Конвертируем в base64
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    img_data = buffer.getvalue()
    img_base64 = base64.b64encode(img_data).decode('utf-8')
    
    return img_base64

def test_fixed_worker():
    """Тестируем исправленный worker"""
    print("🧪 Тестируем исправленный RunPod worker...")
    
    # Создаем тестовое изображение
    print("🎨 Создаем тестовое изображение...")
    image_base64 = create_test_image()
    
    # Формируем запрос
    url = f"https://api.runpod.ai/v2/{RUNPOD_ENDPOINT_ID}/run"
    headers = {
        "Authorization": f"Bearer {RUNPOD_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "input": {
            "image_data": image_base64,
            "task_id": f"test_fixed_{int(time.time())}"
        }
    }
    
    print(f"📤 Отправляем запрос на {RUNPOD_ENDPOINT_ID}...")
    
    try:
        # Отправляем запрос
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        
        result = response.json()
        print(f"✅ Запрос отправлен! Job ID: {result.get('id')}")
        
        # Ждем результат
        job_id = result["id"]
        status_url = f"https://api.runpod.ai/v2/{RUNPOD_ENDPOINT_ID}/status/{job_id}"
        
        print("⏳ Ждем обработки...")
        max_attempts = 30
        attempt = 0
        
        while attempt < max_attempts:
            time.sleep(10)
            attempt += 1
            
            status_response = requests.get(status_url, headers=headers)
            status_response.raise_for_status()
            
            status_data = status_response.json()
            status = status_data.get("status")
            
            print(f"📊 Попытка {attempt}: Статус = {status}")
            
            if status == "COMPLETED":
                output = status_data.get("output", {})
                
                # Проверяем результат
                if "error" in output:
                    print(f"❌ Ошибка worker'а: {output['error']}")
                    return False
                
                if "glb_data" in output and "ply_data" in output:
                    print("✅ УСПЕХ! Worker работает корректно!")
                    print(f"📏 GLB размер: {len(output['glb_data'])} символов")
                    print(f"📏 PLY размер: {len(output['ply_data'])} символов")
                    
                    # Проверяем, что это не mock данные
                    if output['glb_data'] == "mock_glb_data_for_demo_purposes":
                        print("⚠️  Получены mock данные - TRELLIS все еще не работает")
                        return False
                    else:
                        print("🎉 Получены РЕАЛЬНЫЕ 3D данные!")
                        return True
                else:
                    print(f"❌ Неожиданный формат ответа: {output}")
                    return False
                    
            elif status == "FAILED":
                error_msg = status_data.get("error", "Unknown error")
                print(f"❌ Job failed: {error_msg}")
                return False
                
            elif status in ["IN_QUEUE", "IN_PROGRESS"]:
                continue
            else:
                print(f"⚠️  Неизвестный статус: {status}")
                
        print("⏰ Timeout - job не завершился за разумное время")
        return False
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Ошибка запроса: {e}")
        return False
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Тест исправленного RunPod worker'а")
    print("=" * 50)
    
    success = test_fixed_worker()
    
    if success:
        print("\n🎉 ВСЕ РАБОТАЕТ! Worker исправлен!")
    else:
        print("\n💔 Worker все еще имеет проблемы")
        print("📋 Проверьте логи RunPod для диагностики")
