# Деплой на Railway

## Шаги для деплоя

### 1. Подготовка репозитория

Убедитесь, что все изменения зафиксированы в Git:

```bash
git add .
git commit -m "feat: готов к деплою на Railway"
git push origin main
```

### 2. Создание проекта на Railway

1. Перейдите на [railway.app](https://railway.app)
2. Войдите через GitHub аккаунт
3. Нажмите "New Project"
4. Выберите "Deploy from GitHub repo"
5. Выберите репозиторий `Photo_to_3D`

### 3. Настройка переменных окружения

В Railway Dashboard добавьте следующие переменные:

#### Обязательные переменные:
```env
DATABASE_URL=postgresql://username:password@host:port/database
REDIS_URL=redis://host:port/database
JWT_SECRET_KEY=your-super-secret-jwt-key-here
```

#### Дополнительные переменные:
```env
# API Configuration
PROJECT_NAME=Photo to 3D
VERSION=1.0.0
DEBUG=false
API_V1_STR=/api/v1

# TRELLIS Configuration
TRELLIS_MODEL_PATH=microsoft/TRELLIS-image-large
ATTN_BACKEND=flash-attn
SPCONV_ALGO=native

# File Upload
MAX_FILE_SIZE_MB=10

# 3D Generation
GENERATION_TIMEOUT_SECONDS=300
MAX_CONCURRENT_GENERATIONS=3

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_BURST=10

# Stripe (если используется)
STRIPE_SECRET_KEY=sk_live_...
STRIPE_PUBLISHABLE_KEY=pk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
```

### 4. Добавление дополнительных сервисов

#### PostgreSQL Database:
1. В Railway Dashboard нажмите "Add Service"
2. Выберите "PostgreSQL"
3. Скопируйте DATABASE_URL в переменные окружения

#### Redis:
1. В Railway Dashboard нажмите "Add Service"
2. Выберите "Redis"
3. Скопируйте REDIS_URL в переменные окружения

### 5. Настройка домена

1. В настройках проекта перейдите в "Settings"
2. В разделе "Domains" добавьте свой домен
3. Или используйте автоматически сгенерированный домен Railway

### 6. Мониторинг деплоя

1. Следите за логами в разделе "Deployments"
2. Проверьте статус здоровья: `https://your-domain.com/health`
3. Откройте документацию API: `https://your-domain.com/docs`

## Автоматический деплой

После настройки каждый push в ветку `main` будет автоматически деплоиться на Railway.

## Проверка работы

После успешного деплоя проверьте:

```bash
# Health check
curl https://your-domain.com/health

# API documentation
curl https://your-domain.com/docs

# Test generation (с файлом)
curl -X POST "https://your-domain.com/api/v1/generation/generate" \
  -F "image=@test_image.jpg" \
  -F "seed=42"
```

## Мониторинг и логи

### Просмотр логов:
```bash
# В Railway Dashboard -> Deployments -> View Logs
```

### Метрики:
- CPU usage
- Memory usage  
- Network traffic
- Response times

## Troubleshooting

### Частые проблемы:

1. **Ошибка импорта TRELLIS**
   - Убедитесь, что установлены все зависимости
   - Проверьте переменные окружения TRELLIS

2. **Ошибка подключения к БД**
   - Проверьте DATABASE_URL
   - Убедитесь, что PostgreSQL сервис запущен

3. **Ошибка памяти**
   - Увеличьте лимиты памяти в Railway
   - Оптимизируйте загрузку моделей TRELLIS

4. **Timeout ошибки**
   - Увеличьте healthcheckTimeout в railway.json
   - Оптимизируйте время запуска приложения

### Полезные команды:

```bash
# Локальное тестирование с Railway переменными
railway run python -m app.main

# Просмотр переменных окружения
railway variables

# Подключение к базе данных
railway connect postgresql
```

## Масштабирование

Для увеличения производительности:

1. **Увеличьте ресурсы**
   - CPU: 2-4 cores
   - RAM: 4-8 GB
   - Disk: SSD

2. **Оптимизируйте код**
   - Используйте async/await
   - Кэшируйте модели TRELLIS
   - Добавьте connection pooling

3. **Мониторинг**
   - Настройте алерты
   - Отслеживайте метрики
   - Логируйте ошибки

## Стоимость

Примерная стоимость на Railway:
- Starter: $5/месяц
- Pro: $20/месяц  
- Team: $100/месяц

Дополнительные расходы:
- PostgreSQL: $5-20/месяц
- Redis: $5-15/месяц
- GPU (если нужно): $50-200/месяц
