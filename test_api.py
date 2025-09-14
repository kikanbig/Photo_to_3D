#!/usr/bin/env python3
"""
Тест API приложения Photo to 3D
"""
import os
import sys
import asyncio
import requests
from io import BytesIO
from PIL import Image

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def create_test_image():
    """Создать тестовое изображение"""
    # Создаем простое тестовое изображение
    img = Image.new('RGB', (256, 256), color=(73, 109, 137))
    
    # Сохраняем в BytesIO
    img_bytes = BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    
    return img_bytes

def test_health_endpoint():
    """Тест health endpoint"""
    print("🔍 Тестирование /health endpoint...")
    
    try:
        response = requests.get("http://localhost:8002/health", timeout=5)
        print(f"✅ Статус: {response.status_code}")
        print(f"✅ Ответ: {response.json()}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"❌ Ошибка подключения: {e}")
        return False

def test_generation_endpoint():
    """Тест generation endpoint"""
    print("\n🔍 Тестирование /api/v1/generation/generate endpoint...")
    
    try:
        # Создаем тестовое изображение
        test_image = create_test_image()
        
        # Подготавливаем данные для отправки
        files = {
            'image': ('test.png', test_image, 'image/png')
        }
        
        data = {
            'seed': 42,
            'ss_guidance_strength': 7.5,
            'ss_sampling_steps': 12,
            'slat_guidance_strength': 3.0,
            'slat_sampling_steps': 12
        }
        
        response = requests.post(
            "http://localhost:8002/api/v1/generation/generate",
            files=files,
            data=data,
            timeout=30
        )
        
        print(f"✅ Статус: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Task ID: {result.get('task_id')}")
            print(f"✅ Статус: {result.get('status')}")
            return result.get('task_id')
        else:
            print(f"❌ Ошибка: {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Ошибка подключения: {e}")
        return None

def test_status_endpoint(task_id):
    """Тест status endpoint"""
    if not task_id:
        return
    
    print(f"\n🔍 Тестирование /api/v1/generation/status/{task_id} endpoint...")
    
    try:
        response = requests.get(
            f"http://localhost:8002/api/v1/generation/status/{task_id}",
            timeout=5
        )
        
        print(f"✅ Статус: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Статус генерации: {result.get('status')}")
            print(f"✅ Сообщение: {result.get('message')}")
            
            # Тестируем ссылки на скачивание
            if result.get('glb_url'):
                print(f"✅ GLB URL: {result.get('glb_url')}")
            if result.get('ply_url'):
                print(f"✅ PLY URL: {result.get('ply_url')}")
        else:
            print(f"❌ Ошибка: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Ошибка подключения: {e}")

def test_download_endpoints(task_id):
    """Тест download endpoints"""
    if not task_id:
        return
    
    print(f"\n🔍 Тестирование download endpoints...")
    
    # Тест GLB download
    try:
        response = requests.get(
            f"http://localhost:8002/api/v1/generation/download/{task_id}/glb",
            timeout=5
        )
        print(f"✅ GLB Download статус: {response.status_code}")
        if response.status_code == 200:
            print(f"✅ GLB размер: {len(response.content)} байт")
    except Exception as e:
        print(f"❌ GLB Download ошибка: {e}")
    
    # Тест PLY download
    try:
        response = requests.get(
            f"http://localhost:8002/api/v1/generation/download/{task_id}/ply",
            timeout=5
        )
        print(f"✅ PLY Download статус: {response.status_code}")
        if response.status_code == 200:
            print(f"✅ PLY размер: {len(response.content)} байт")
    except Exception as e:
        print(f"❌ PLY Download ошибка: {e}")

def main():
    """Основная функция тестирования"""
    print("🧪 Запуск тестов API Photo to 3D\n")
    
    # Тест 1: Health endpoint
    if not test_health_endpoint():
        print("\n❌ Сервер недоступен. Убедитесь, что приложение запущено на порту 8002")
        return
    
    # Тест 2: Generation endpoint
    task_id = test_generation_endpoint()
    
    # Тест 3: Status endpoint
    test_status_endpoint(task_id)
    
    # Тест 4: Download endpoints
    test_download_endpoints(task_id)
    
    print("\n🎉 Тестирование завершено!")

if __name__ == "__main__":
    main()
