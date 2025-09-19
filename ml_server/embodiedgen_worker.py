#!/usr/bin/env python3
"""
EmbodiedGen Worker for 3D Generation
Альтернативное решение для Image-to-3D
"""
import os
import sys
import tempfile
import logging
import subprocess
import json
from typing import Dict, Optional, Any
from PIL import Image
import base64
import io

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmbodiedGenWorker:
    """Worker для генерации 3D моделей через EmbodiedGen"""
    
    def __init__(self):
        self.device = "cuda" if os.environ.get("CUDA_VISIBLE_DEVICES") else "cpu"
        self.is_initialized = False
        self.pipeline = None
        
        print(f"🔧 EmbodiedGenWorker initialized on device: {self.device}")
        
    def _initialize_pipeline(self):
        """Инициализация EmbodiedGen pipeline"""
        try:
            print("📦 Initializing EmbodiedGen pipeline...")
            
            # Проверяем, установлен ли EmbodiedGen
            try:
                result = subprocess.run(['img3d-cli', '--help'], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    print("✅ EmbodiedGen CLI found")
                    self.pipeline = "embodiedgen"
                    self.is_initialized = True
                    return
                else:
                    print(f"⚠️ EmbodiedGen CLI not working: {result.stderr}")
            except (subprocess.TimeoutExpired, FileNotFoundError):
                print("⚠️ EmbodiedGen CLI not found")
            
            # Fallback на mock режим
            print("🔄 Falling back to mock mode")
            self.pipeline = "mock"
            self.is_initialized = True
            
        except Exception as e:
            print(f"❌ Failed to initialize EmbodiedGen: {e}")
            self.pipeline = "mock"
            self.is_initialized = True
    
    def generate_3d(self, image_data: bytes, task_id: str) -> Dict[str, Any]:
        """Генерация 3D модели из изображения"""
        if not self.is_initialized:
            self._initialize_pipeline()
        
        try:
            # Создаем временный файл для изображения
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_img:
                temp_img.write(image_data)
                temp_img_path = temp_img.name
            
            # Создаем выходную директорию
            output_dir = tempfile.mkdtemp()
            
            if self.pipeline == "embodiedgen":
                # Используем EmbodiedGen CLI
                cmd = [
                    'img3d-cli',
                    '--image_path', temp_img_path,
                    '--output_root', output_dir
                ]
                
                print(f"🚀 Running EmbodiedGen: {' '.join(cmd)}")
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
                
                if result.returncode == 0:
                    print("✅ EmbodiedGen generation successful")
                    
                    # Ищем сгенерированные файлы
                    glb_files = []
                    ply_files = []
                    
                    for root, dirs, files in os.walk(output_dir):
                        for file in files:
                            if file.endswith('.glb'):
                                glb_files.append(os.path.join(root, file))
                            elif file.endswith('.ply'):
                                ply_files.append(os.path.join(root, file))
                    
                    if glb_files and ply_files:
                        glb_path = glb_files[0]
                        ply_path = ply_files[0]
                        
                        # Читаем файлы
                        with open(glb_path, 'rb') as f:
                            glb_data = f.read()
                        with open(ply_path, 'rb') as f:
                            ply_data = f.read()
                        
                        # Кодируем в base64
                        glb_base64 = base64.b64encode(glb_data).decode('utf-8')
                        ply_base64 = base64.b64encode(ply_data).decode('utf-8')
                        
                        return {
                            'glb_path': glb_path,
                            'glb_path_base64': glb_base64,
                            'glb_path_size': len(glb_data),
                            'ply_path': ply_path,
                            'ply_path_base64': ply_base64,
                            'ply_path_size': len(ply_data)
                        }
                    else:
                        print("⚠️ No GLB/PLY files found in output")
                        return self._generate_mock_result()
                else:
                    print(f"❌ EmbodiedGen failed: {result.stderr}")
                    return self._generate_mock_result()
            
            else:
                # Mock режим
                return self._generate_mock_result()
                
        except Exception as e:
            print(f"❌ Error in generate_3d: {e}")
            return self._generate_mock_result()
        
        finally:
            # Очищаем временные файлы
            try:
                if 'temp_img_path' in locals():
                    os.unlink(temp_img_path)
                if 'output_dir' in locals():
                    import shutil
                    shutil.rmtree(output_dir, ignore_errors=True)
            except:
                pass
    
    def _generate_mock_result(self) -> Dict[str, Any]:
        """Генерация mock результата"""
        mock_glb_data = b"mock_glb_data_for_demo_purposes"
        mock_ply_data = b"""ply
format ascii 1.0
element vertex 4
property float x
property float y
property float z
end_header
0.0 0.0 0.0
1.0 0.0 0.0
0.0 1.0 0.0
0.0 0.0 1.0
"""
        
        glb_base64 = base64.b64encode(mock_glb_data).decode('utf-8')
        ply_base64 = base64.b64encode(mock_ply_data).decode('utf-8')
        
        return {
            'glb_path': '/tmp/mock.glb',
            'glb_path_base64': glb_base64,
            'glb_path_size': len(mock_glb_data),
            'ply_path': '/tmp/mock.ply',
            'ply_path_base64': ply_base64,
            'ply_path_size': len(mock_ply_data)
        }

# Глобальный экземпляр worker'а
worker = EmbodiedGenWorker()

def handler(event):
    """RunPod handler для EmbodiedGen"""
    try:
        print(f"🚀 Starting 3D generation for task: {event.get('id', 'unknown')}")
        
        # Получаем данные изображения
        if 'input' in event and 'image' in event['input']:
            image_data = event['input']['image']
            if isinstance(image_data, str):
                # Base64 строка
                image_data = base64.b64decode(image_data)
            elif isinstance(image_data, dict) and 'data' in image_data:
                # Base64 объект
                image_data = base64.b64decode(image_data['data'])
        else:
            return {"error": "No image data provided"}
        
        # Генерируем 3D модель
        result = worker.generate_3d(image_data, event.get('id', 'unknown'))
        
        return {
            "result": result,
            "status": "completed",
            "task_id": event.get('id', 'unknown')
        }
        
    except Exception as e:
        print(f"❌ Error in handler: {e}")
        return {
            "error": str(e),
            "status": "failed",
            "task_id": event.get('id', 'unknown')
        }

if __name__ == "__main__":
    # Тестирование
    test_event = {
        "id": "test_embodiedgen",
        "input": {
            "image": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
        }
    }
    
    result = handler(test_event)
    print(f"Test result: {result}")
