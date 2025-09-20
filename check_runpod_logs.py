#!/usr/bin/env python3
"""
Проверка логов RunPod для Job ID
"""
import os
import requests
import json

# Учетные данные RunPod
RUNPOD_API_KEY = os.getenv("RUNPOD_API_KEY")
RUNPOD_ENDPOINT_ID = os.getenv("RUNPOD_ENDPOINT_ID")

def check_job_logs(job_id: str):
    """Проверить логи конкретного Job'а"""
    print(f"🔍 Проверяем логи для Job ID: {job_id}")
    
    # URL для получения статуса Job'а
    url = f"https://api.runpod.ai/v2/{RUNPOD_ENDPOINT_ID}/status/{job_id}"
    
    headers = {
        "Authorization": f"Bearer {RUNPOD_API_KEY}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        print(f"✅ Статус Job'а: {data.get('status', 'unknown')}")
        
        # Проверяем есть ли логи
        if 'logs' in data:
            logs = data['logs']
            print(f"📋 Логи найдены ({len(logs)} строк):")
            print("=" * 50)
            for log in logs[-20:]:  # Последние 20 строк
                print(log)
            print("=" * 50)
        else:
            print("❌ Логи не найдены в ответе")
            
        # Проверяем результат
        if 'result' in data:
            result = data['result']
            print(f"📊 Результат: {json.dumps(result, indent=2)}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Ошибка запроса: {e}")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    if not RUNPOD_API_KEY or not RUNPOD_ENDPOINT_ID:
        print("❌ RUNPOD_API_KEY и RUNPOD_ENDPOINT_ID обязательны")
        exit(1)
    
    # Проверяем логи для последнего Job'а
    job_id = "27f37309-7034-4f8a-ac94-dde75a95e40f-e2"
    check_job_logs(job_id)
