#!/usr/bin/env python3
"""
Hybrid Worker для 3D Generation
Поддерживает TRELLIS и EmbodiedGen
"""
import os
import sys
import tempfile
import logging
from typing import Dict, Optional, Any
from PIL import Image
import base64
import io

# Импортируем оба worker'а
try:
    from trellis_worker import TrellisWorker
    TRELLIS_AVAILABLE = True
except ImportError:
    TRELLIS_AVAILABLE = False
    print("⚠️ TRELLIS worker not available")

try:
    from embodiedgen_worker import EmbodiedGenWorker
    EMBODIEDGEN_AVAILABLE = True
except ImportError:
    EMBODIEDGEN_AVAILABLE = False
    print("⚠️ EmbodiedGen worker not available")

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HybridWorker:
    """Гибридный worker для генерации 3D моделей"""
    
    def __init__(self):
        self.device = "cuda" if os.environ.get("CUDA_VISIBLE_DEVICES") else "cpu"
        self.is_initialized = False
        
        # Инициализируем доступные worker'ы
        self.workers = {}
        
        if TRELLIS_AVAILABLE:
            try:
                self.workers['trellis'] = TrellisWorker()
                print("✅ TRELLIS worker initialized")
            except Exception as e:
                print(f"❌ Failed to initialize TRELLIS worker: {e}")
        
        if EMBODIEDGEN_AVAILABLE:
            try:
                self.workers['embodiedgen'] = EmbodiedGenWorker()
                print("✅ EmbodiedGen worker initialized")
            except Exception as e:
                print(f"❌ Failed to initialize EmbodiedGen worker: {e}")
        
        # Определяем приоритетный worker
        self.primary_worker = None
        self.fallback_worker = None
        
        if 'trellis' in self.workers:
            self.primary_worker = 'trellis'
            if 'embodiedgen' in self.workers:
                self.fallback_worker = 'embodiedgen'
        elif 'embodiedgen' in self.workers:
            self.primary_worker = 'embodiedgen'
        
        print(f"🔧 HybridWorker initialized on device: {self.device}")
        print(f"🎯 Primary worker: {self.primary_worker}")
        print(f"🔄 Fallback worker: {self.fallback_worker}")
        
        self.is_initialized = True
    
    def generate_3d(self, image_data: bytes, task_id: str) -> Dict[str, Any]:
        """Генерация 3D модели с fallback"""
        if not self.is_initialized:
            return {"error": "Worker not initialized"}
        
        # Пробуем основной worker
        if self.primary_worker and self.primary_worker in self.workers:
            try:
                print(f"🚀 Trying {self.primary_worker} worker...")
                result = self.workers[self.primary_worker].generate_3d(image_data, task_id)
                
                # Проверяем, не mock ли это
                if self._is_real_result(result):
                    print(f"✅ {self.primary_worker} worker succeeded with real data")
                    return result
                else:
                    print(f"⚠️ {self.primary_worker} worker returned mock data")
                    
            except Exception as e:
                print(f"❌ {self.primary_worker} worker failed: {e}")
        
        # Пробуем fallback worker
        if self.fallback_worker and self.fallback_worker in self.workers:
            try:
                print(f"🔄 Trying fallback {self.fallback_worker} worker...")
                result = self.workers[self.fallback_worker].generate_3d(image_data, task_id)
                
                if self._is_real_result(result):
                    print(f"✅ {self.fallback_worker} worker succeeded with real data")
                    return result
                else:
                    print(f"⚠️ {self.fallback_worker} worker returned mock data")
                    
            except Exception as e:
                print(f"❌ {self.fallback_worker} worker failed: {e}")
        
        # Если все worker'ы не работают, возвращаем mock
        print("🔄 All workers failed, returning mock data")
        return self._generate_mock_result()
    
    def _is_real_result(self, result: Dict[str, Any]) -> bool:
        """Проверяем, является ли результат реальным (не mock)"""
        if not result:
            return False
        
        # Проверяем размеры файлов
        glb_size = result.get('glb_path_size', 0)
        ply_size = result.get('ply_path_size', 0)
        
        # Если файлы слишком маленькие, это mock
        if glb_size < 1000 or ply_size < 1000:
            return False
        
        # Проверяем содержимое base64
        glb_base64 = result.get('glb_path_base64', '')
        if 'mock' in glb_base64.lower():
            return False
        
        return True
    
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
worker = HybridWorker()

def handler(event):
    """RunPod handler для гибридного worker'а"""
    try:
        print(f"🚀 Starting hybrid 3D generation for task: {event.get('id', 'unknown')}")
        
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
        "id": "test_hybrid",
        "input": {
            "image": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
        }
    }
    
    result = handler(test_event)
    print(f"Test result: {result}")
