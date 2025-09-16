"""
Прямое тестирование RunPod endpoint после деплоя
"""
import requests
import base64
import json
import time

def test_runpod_endpoint():
    """
    Тест RunPod endpoint напрямую
    """
    # Эти данные получим после успешного деплоя
    ENDPOINT_ID = "z34poz9n7a9487"  # твой endpoint ID
    API_KEY = "RP-..."  # нужно получить из RunPod Dashboard
    
    if API_KEY == "RP-...":
        print("❌ Нужно получить API ключ из RunPod Dashboard")
        print("   Settings → API Keys → Create New Key")
        return
    
    # URL для RunPod Serverless API
    url = f"https://api.runpod.ai/v2/{ENDPOINT_ID}/run"
    
    # Заголовки
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Тестовые данные (можно использовать любое изображение)
    test_image_b64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="  # 1x1 pixel PNG
    
    # Payload для RunPod
    payload = {
        "input": {
            "image_data": test_image_b64,
            "image_format": "png",
            "output_format": "glb",
            "quality": "medium"
        }
    }
    
    try:
        print("🚀 Отправляем запрос в RunPod...")
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Запрос принят!")
            print(f"📋 Job ID: {result.get('id', 'не найден')}")
            print(f"📊 Status: {result.get('status', 'неизвестно')}")
            
            if result.get('status') == 'IN_QUEUE':
                print("⏳ Задача в очереди, проверяем статус...")
                job_id = result['id']
                check_job_status(job_id, API_KEY)
            elif result.get('status') == 'COMPLETED':
                print("🎉 Задача выполнена!")
                print(f"📁 Результат: {result.get('output', {})}")
            
        else:
            print(f"❌ Ошибка HTTP {response.status_code}")
            print(f"📄 Ответ: {response.text}")
            
    except requests.exceptions.Timeout:
        print("⏰ Таймаут запроса")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

def check_job_status(job_id: str, api_key: str, max_attempts: int = 10):
    """
    Проверяет статус задачи в RunPod
    """
    status_url = f"https://api.runpod.ai/v2/{job_id}/status"
    headers = {
        "Authorization": f"Bearer {api_key}",
    }
    
    for attempt in range(max_attempts):
        try:
            response = requests.get(status_url, headers=headers)
            if response.status_code == 200:
                result = response.json()
                status = result.get('status', 'unknown')
                print(f"📊 Попытка {attempt + 1}: {status}")
                
                if status == 'COMPLETED':
                    print("🎉 Задача выполнена!")
                    output = result.get('output', {})
                    print(f"📁 GLB URL: {output.get('glb_url', 'не найден')}")
                    print(f"🖼️ Preview: {output.get('preview_url', 'не найден')}")
                    break
                elif status == 'FAILED':
                    print("❌ Задача провалилась!")
                    print(f"🔍 Ошибка: {result.get('error', 'неизвестная')}")
                    break
                    
            time.sleep(5)  # Ждем 5 секунд между проверками
            
        except Exception as e:
            print(f"❌ Ошибка проверки статуса: {e}")
            break

if __name__ == "__main__":
    print("🧪 Тестирование RunPod endpoint")
    print("=" * 40)
    test_runpod_endpoint()
