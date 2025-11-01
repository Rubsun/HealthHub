# HealthHub - Personal Health Monitoring System

Микросервисная система мониторинга здоровья и активности.

## Архитектура

- **api-gateway** - точка входа, роутинг и аутентификация
- **users-service** - управление пользователями
- **health-service** - метрики здоровья, активности и рекомендации
- **nutrition-service** - питание и продукты (интеграция с OpenFoodFacts)
- **integrations-service** - интеграция с OpenWeather API

## Технологии

- Python 3.11+
- FastAPI
- FastStream + RabbitMQ
- PostgreSQL + SQLAlchemy 2.x + Alembic
- Docker + docker-compose
- pytest + coverage

## Запуск

1. Скопируйте `.env.example` в `.env` и заполните необходимые переменные:
   ```bash
   cp .env.example .env
   ```

2. Запустите все сервисы:
   ```bash
   docker-compose up
   ```

3. API Gateway будет доступен на http://localhost:8000
   - Swagger документация: http://localhost:8000/docs

## Миграции

Миграции запускаются автоматически при старте контейнеров. Для ручного запуска:

```bash
make migrate-all
```

## Тестирование

```bash
make test
```

## Структура проекта

```
.
├── services/
│   ├── api-gateway/
│   ├── users-service/
│   ├── health-service/
│   ├── nutrition-service/
│   └── integrations-service/
├── docker-compose.yml
├── Makefile
└── README.md
```



