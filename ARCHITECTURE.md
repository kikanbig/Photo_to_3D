# Архитектура Photo_to_3D

## Обзор системы

Веб-сервис для генерации 3D моделей из фотографий с монетизацией, основанный на Microsoft TRELLIS.

## Техническая архитектура

### 1. Основные компоненты

#### Backend (FastAPI)
- **API Server**: FastAPI для REST API и WebSocket
- **3D Generation Service**: Интеграция с TRELLIS
- **Payment Service**: Stripe для обработки платежей
- **User Management**: Аутентификация и авторизация
- **File Storage**: S3-совместимое хранилище для файлов
- **Queue System**: Redis для очередей задач

#### Frontend (React/Next.js)
- **Web Interface**: Загрузка изображений и просмотр результатов
- **3D Viewer**: Three.js для просмотра GLB моделей
- **Payment Integration**: Stripe Elements для платежей
- **User Dashboard**: Управление подписками и историей

#### Telegram Bot (опционально)
- **Bot API**: python-telegram-bot
- **File Handling**: Обработка изображений из Telegram
- **Payment Integration**: Telegram Payments API

### 2. Интеграция с TRELLIS

#### Модели
- **TRELLIS-image-large**: Основная модель для image-to-3D (1.2B параметров)
- **TRELLIS-text-base**: Для текстовых промптов (342M параметров)

#### Pipeline
```python
# Основной pipeline
pipeline = TrellisImageTo3DPipeline.from_pretrained("microsoft/TRELLIS-image-large")
outputs = pipeline.run(
    image,
    seed=seed,
    formats=["gaussian", "mesh"],
    sparse_structure_sampler_params={
        "steps": 12,
        "cfg_strength": 7.5,
    },
    slat_sampler_params={
        "steps": 12,
        "cfg_strength": 3.0,
    },
)
```

#### Выходные форматы
- **GLB**: Основной формат для веб-просмотра
- **PLY**: 3D Gaussian файлы
- **MP4**: Видео превью

### 3. Монетизация

#### Модели оплаты
1. **Pay-per-use**: $0.50-2.00 за генерацию
2. **Subscription**: 
   - Basic: $9.99/месяц (50 генераций)
   - Pro: $19.99/месяц (200 генераций)
   - Enterprise: $49.99/месяц (1000 генераций)
3. **Credits**: Покупка пакетов кредитов

#### Интеграции
- **Stripe**: Основная платежная система
- **Telegram Payments**: Для бота
- **Webhook**: Обновление статуса подписки

### 4. Инфраструктура

#### Railway Deployment
- **Web Service**: FastAPI приложение
- **Worker**: Отдельный сервис для 3D генерации
- **Redis**: Очереди и кэширование
- **PostgreSQL**: База данных пользователей
- **S3 Storage**: Файловое хранилище

#### Переменные окружения
```env
# TRELLIS
TRELLIS_MODEL_PATH=microsoft/TRELLIS-image-large
CUDA_VISIBLE_DEVICES=0

# Database
DATABASE_URL=postgresql://...

# Redis
REDIS_URL=redis://...

# Storage
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
S3_BUCKET=...

# Stripe
STRIPE_SECRET_KEY=...
STRIPE_WEBHOOK_SECRET=...

# Telegram
TELEGRAM_BOT_TOKEN=...
```

### 5. API Endpoints

#### Основные
- `POST /api/generate` - Генерация 3D модели
- `GET /api/models/{id}` - Получение модели
- `GET /api/models/{id}/download` - Скачивание GLB
- `POST /api/payment/create` - Создание платежа
- `POST /api/payment/webhook` - Webhook Stripe

#### Пользовательские
- `POST /api/auth/register` - Регистрация
- `POST /api/auth/login` - Вход
- `GET /api/user/profile` - Профиль пользователя
- `GET /api/user/subscription` - Подписка
- `GET /api/user/history` - История генераций

### 6. Очереди и обработка

#### Redis Queue
- **generate_queue**: Очередь генерации 3D
- **email_queue**: Очередь уведомлений
- **cleanup_queue**: Очистка временных файлов

#### Worker Process
```python
# Обработка задач генерации
def process_generation_task(task_id, image_path, user_id):
    # 1. Загрузка изображения
    # 2. Генерация 3D модели
    # 3. Сохранение результатов
    # 4. Уведомление пользователя
    # 5. Очистка временных файлов
```

### 7. Безопасность

#### Аутентификация
- JWT токены для API
- Telegram WebApp для бота
- Rate limiting (100 запросов/час)

#### Валидация
- Проверка размера изображений (max 10MB)
- Валидация форматов (PNG, JPG, WEBP)
- Проверка подписок перед генерацией

#### Мониторинг
- Логирование всех операций
- Метрики производительности
- Алерты при ошибках

### 8. Масштабирование

#### Горизонтальное
- Несколько worker процессов
- Load balancer для API
- Репликация базы данных

#### Вертикальное
- GPU с 16GB+ памяти
- SSD для быстрого доступа к файлам
- Кэширование моделей в памяти

### 9. Мониторинг и аналитика

#### Метрики
- Время генерации 3D моделей
- Успешность генерации
- Использование ресурсов
- Конверсия платежей

#### Логирование
- Структурированные логи (JSON)
- Централизованный сбор логов
- Алерты при критических ошибках

### 10. Развертывание

#### Railway
- Автоматический деплой из GitHub
- Переменные окружения через dashboard
- Мониторинг через Railway console

#### CI/CD
- GitHub Actions для тестирования
- Автоматические тесты перед деплоем
- Rollback при ошибках
