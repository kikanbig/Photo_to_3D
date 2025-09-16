"""
Скрипт для генерации и скачивания GLB файлов
"""
import os
import requests
import base64
import json
from datetime import datetime

def generate_and_download():
    """
    Генерирует 3D модель и скачивает GLB файл
    """
    
    # Настройки
    railway_url = "https://web-production-24c39.up.railway.app"
    photo_path = "/Users/kikanbig/Мои стартапы/Photo_to_3D/Фото для моделей/4879854.jpg"
    output_dir = "/Users/kikanbig/Мои стартапы/Photo_to_3D/Generated_Models"
    
    print("🧪 Генерация и скачивание 3D модели")
    print("=" * 40)
    
    # Создаем папку для результатов
    os.makedirs(output_dir, exist_ok=True)
    
    # Проверяем фото
    if not os.path.exists(photo_path):
        print(f"❌ Фото не найдено: {photo_path}")
        return
    
    print(f"📸 Используем фото: {os.path.basename(photo_path)}")
    
    try:
        # Отправляем запрос на генерацию
        with open(photo_path, "rb") as f:
            files = {'image': ('photo.jpg', f, 'image/jpeg')}
            
            print("🚀 Отправляем запрос в Railway...")
            response = requests.post(
                f"{railway_url}/api/v1/generate",
                files=files,
                timeout=300
            )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Генерация завершена!")
            
            # Извлекаем данные
            task_id = result.get('task_id', 'unknown')
            execution_time = result.get('execution_time', 0)
            result_data = result.get('result', {}).get('result', {})
            
            print(f"📋 Task ID: {task_id}")
            print(f"⏱️ Время генерации: {execution_time} секунд")
            
            # Скачиваем GLB файл
            if 'glb_path_base64' in result_data:
                glb_base64 = result_data['glb_path_base64']
                glb_size = result_data.get('glb_path_size', 0)
                
                print(f"📁 GLB размер: {glb_size:,} bytes")
                
                # Декодируем и сохраняем
                glb_data = base64.b64decode(glb_base64)
                
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                glb_filename = f"model_{timestamp}_{task_id[:8]}.glb"
                glb_path = os.path.join(output_dir, glb_filename)
                
                with open(glb_path, "wb") as f:
                    f.write(glb_data)
                
                print(f"✅ GLB файл сохранен: {glb_path}")
                
                # Также сохраняем PLY если есть
                if 'ply_path_base64' in result_data:
                    ply_base64 = result_data['ply_path_base64']
                    ply_size = result_data.get('ply_path_size', 0)
                    
                    print(f"📁 PLY размер: {ply_size:,} bytes")
                    
                    ply_data = base64.b64decode(ply_base64)
                    ply_filename = f"model_{timestamp}_{task_id[:8]}.ply"
                    ply_path = os.path.join(output_dir, ply_filename)
                    
                    with open(ply_path, "wb") as f:
                        f.write(ply_data)
                    
                    print(f"✅ PLY файл сохранен: {ply_path}")
                
                print(f"\n🎉 Файлы сохранены в папке: {output_dir}")
                print(f"📱 Открой GLB файл в любом 3D вьювере!")
                
            else:
                print("❌ GLB данные не найдены в ответе")
                print(f"📄 Полный ответ: {json.dumps(result, indent=2)}")
                
        else:
            print(f"❌ Ошибка API: {response.status_code}")
            print(f"📄 Ответ: {response.text}")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    generate_and_download()
