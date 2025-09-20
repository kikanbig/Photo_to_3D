#!/usr/bin/env python3
"""
Тест Gradio API для TRELLIS
"""
import os
import sys
from gradio_client import Client, handle_file
from PIL import Image
import io
import base64

def test_gradio_trellis():
    """Тестируем Gradio API для TRELLIS"""
    print("🚀 Тест Gradio API для TRELLIS")
    print("=" * 50)
    
    try:
        # Создаем клиент
        print("🔗 Подключаемся к Gradio API...")
        client = Client("trellis-community/TRELLIS")
        print("✅ Подключение успешно!")
        
        # Создаем тестовое изображение
        print("🎨 Создаем тестовое изображение...")
        img = Image.new('RGB', (512, 512), color='red')
        
        # Сохраняем во временный файл
        temp_path = "/tmp/test_image.png"
        img.save(temp_path)
        print(f"✅ Изображение сохранено: {temp_path}")
        
        # Тестируем preprocess_image
        print("🔄 Тестируем preprocess_image...")
        try:
            result = client.predict(
                image=handle_file(temp_path),
                api_name="/preprocess_image"
            )
            print(f"✅ preprocess_image успешно: {result}")
        except Exception as e:
            print(f"❌ Ошибка preprocess_image: {e}")
        
        # Тестируем generate_and_extract_glb с URL
        print("🔄 Тестируем generate_and_extract_glb с URL...")
        try:
            result = client.predict(
                image=handle_file('https://raw.githubusercontent.com/gradio-app/gradio/main/test/test_files/bus.png'),
                multiimages=[],
                seed=42,
                ss_guidance_strength=7.5,
                ss_sampling_steps=12,
                slat_guidance_strength=3,
                slat_sampling_steps=12,
                multiimage_algo="stochastic",
                mesh_simplify=0.95,
                texture_size=1024,
                api_name="/generate_and_extract_glb"
            )
            print(f"✅ generate_and_extract_glb успешно!")
            print(f"📊 Результат: {len(result)} элементов")
            
            if len(result) >= 3:
                video_path = result[0]
                glb_path = result[1]
                download_path = result[2]
                
                print(f"🎥 Видео: {video_path}")
                print(f"📦 GLB: {glb_path}")
                print(f"⬇️ Скачать: {download_path}")
                
                # Проверяем размер GLB файла
                if os.path.exists(glb_path):
                    size = os.path.getsize(glb_path)
                    print(f"📏 Размер GLB: {size} байт")
                    
                    if size > 1000:  # Больше 1KB
                        print("🎉 РЕАЛЬНАЯ ГЕНЕРАЦИЯ! Файл достаточно большой!")
                    else:
                        print("⚠️ Возможно mock данные, файл слишком маленький")
                else:
                    print("❌ GLB файл не найден")
            
        except Exception as e:
            print(f"❌ Ошибка generate_and_extract_glb: {e}")
            import traceback
            traceback.print_exc()
        
        # Очищаем временный файл
        if os.path.exists(temp_path):
            os.remove(temp_path)
            print("🧹 Временный файл удален")
            
    except Exception as e:
        print(f"❌ Общая ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_gradio_trellis()
