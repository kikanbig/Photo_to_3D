# TRELLIS ML Server for RunPod

Этот сервер обрабатывает запросы на генерацию 3D моделей с помощью TRELLIS на RunPod Serverless.

## Структура

- `handler.py` - Основной обработчик RunPod запросов
- `trellis_worker.py` - TRELLIS worker для генерации 3D
- `Dockerfile` - Docker образ с TRELLIS
- `requirements.txt` - Python зависимости

## Настройка RunPod

### Repository Settings:
```
Repository: Photo_to_3D
Branch: main
Dockerfile Path: ml_server/Dockerfile
Build Context: ml_server/
```

### Container Settings:
```
Container Start Command: python handler.py
Container Disk: 15 GB
Expose HTTP Ports: 8000
```

### Environment Variables:
```
PYTHONPATH=/workspace
CUDA_VISIBLE_DEVICES=0
TRELLIS_MODEL_PATH=microsoft/TRELLIS-image-large
ATTN_BACKEND=flash-attn
SPCONV_ALGO=native
```

### Optional S3 Settings:
```
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
S3_BUCKET=your-bucket-name
```

## API Format

### Input:
```json
{
  "input": {
    "image_url": "https://example.com/image.jpg",
    "task_id": "uuid-here",
    "webhook_url": "https://your-railway-app.com/webhook",
    "parameters": {
      "seed": 42,
      "ss_guidance_strength": 7.5,
      "ss_sampling_steps": 12,
      "slat_guidance_strength": 3.0,
      "slat_sampling_steps": 12
    }
  }
}
```

### Output:
```json
{
  "task_id": "uuid-here",
  "status": "completed",
  "result": {
    "glb_path": "/tmp/model.glb",
    "ply_path": "/tmp/model.ply",
    "glb_url": "https://s3.../model.glb",
    "ply_url": "https://s3.../model.ply"
  }
}
```

## Архитектура

```
Railway API → RunPod Queue → TRELLIS Generation → S3 Upload → Webhook
     ↓              ↓              ↓                ↓           ↓
Создает задачу   Запускает      Генерирует       Сохраняет   Уведомляет
в PostgreSQL     контейнер      3D модель        файлы       Railway
```
