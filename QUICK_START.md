# Быстрый старт Photo to 3D

## ✅ Что уже готово

1. **Виртуальное окружение** - создано и активировано
2. **Структура проекта** - полная архитектура FastAPI приложения
3. **Базовые зависимости** - FastAPI, Pydantic, Structlog установлены
4. **Конфигурация** - настройки через переменные окружения
5. **API endpoints** - заготовки для всех основных функций
6. **Модели данных** - Pydantic модели для генерации 3D
7. **Сервисы** - TRELLIS интеграция и генерация 3D
8. **Документация** - README, архитектура, инструкции

## 🚀 Следующие шаги

### 1. Установка TRELLIS зависимостей

```bash
# Активируйте виртуальное окружение
source venv/bin/activate

# Установите PyTorch (выберите версию для вашей системы)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Установите остальные зависимости
pip install -r requirements.txt
```

### 2. Настройка переменных окружения

Создайте файл `.env` в корне проекта:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/photo_to_3d

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT Authentication
JWT_SECRET_KEY=your-super-secret-jwt-key-here

# TRELLIS Configuration
TRELLIS_MODEL_PATH=microsoft/TRELLIS-image-large
CUDA_VISIBLE_DEVICES=0
ATTN_BACKEND=flash-attn
SPCONV_ALGO=native

# API Configuration
API_V1_STR=/api/v1
PROJECT_NAME=Photo to 3D
VERSION=1.0.0
DEBUG=True
```

### 3. Запуск приложения

```bash
# Активируйте виртуальное окружение
source venv/bin/activate

# Запустите приложение
python -m app.main
```

Приложение будет доступно по адресу: http://localhost:8000

### 4. Тестирование API

```bash
# Проверка здоровья приложения
curl http://localhost:8000/health

# Генерация 3D модели (после настройки TRELLIS)
curl -X POST "http://localhost:8000/api/v1/generation/generate" \
  -F "image=@your_image.jpg"
```

## 📁 Структура проекта

```
Photo_to_3D/
├── app/                    # Основное приложение
│   ├── api/v1/            # API endpoints
│   │   └── endpoints/     # Конкретные endpoints
│   ├── core/              # Конфигурация и база данных
│   ├── models/            # Pydantic модели
│   └── services/          # Бизнес-логика
├── frontend/              # React frontend (будущее)
├── telegram_bot/          # Telegram bot (будущее)
├── tests/                 # Тесты
├── requirements.txt       # Python зависимости
├── railway.json          # Конфигурация Railway
└── README.md             # Документация
```

## 🔧 Разработка

### Добавление новых endpoints

1. Создайте файл в `app/api/v1/endpoints/`
2. Добавьте router в `app/api/v1/api.py`
3. Обновите модели в `app/models/`

### Добавление новых сервисов

1. Создайте файл в `app/services/`
2. Импортируйте в нужных местах
3. Добавьте в dependency injection

### Тестирование

```bash
# Запуск тестов
python simple_test.py

# Запуск полных тестов (после установки всех зависимостей)
pytest tests/
```

## 🚀 Деплой на Railway

1. **Подключите GitHub репозиторий к Railway**
2. **Настройте переменные окружения в Railway dashboard**
3. **Деплой произойдет автоматически при пуше в main ветку**

### Переменные окружения для Railway

- `DATABASE_URL` - PostgreSQL от Railway
- `REDIS_URL` - Redis от Railway  
- `JWT_SECRET_KEY` - ваш секретный ключ
- `TRELLIS_MODEL_PATH` - путь к модели TRELLIS
- `STRIPE_SECRET_KEY` - ключ Stripe для платежей

## 💡 Полезные команды

```bash
# Активация окружения
source venv/bin/activate

# Установка зависимостей
pip install -r requirements.txt

# Запуск приложения
python -m app.main

# Форматирование кода
black app/
isort app/

# Проверка типов
mypy app/
```

## 🆘 Решение проблем

### Ошибка импорта TRELLIS
- Убедитесь, что установлен PyTorch
- Проверьте CUDA совместимость
- Установите все зависимости из requirements.txt

### Ошибка подключения к базе данных
- Проверьте DATABASE_URL
- Убедитесь, что PostgreSQL запущен
- Проверьте права доступа

### Ошибка Redis
- Проверьте REDIS_URL
- Убедитесь, что Redis запущен
- Проверьте подключение

## 📞 Поддержка

При возникновении проблем:
1. Проверьте логи приложения
2. Убедитесь в правильности переменных окружения
3. Проверьте совместимость версий Python и зависимостей
4. Обратитесь к документации FastAPI и TRELLIS
