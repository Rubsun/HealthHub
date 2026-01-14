# HealthHub - Personal Health Monitoring System

Микросервисная система мониторинга здоровья и активности.

## Архитектура
### Сервисы

- **api-gateway** - точка входа, роутинг, JWT аутентификация
- **users-service** - управление пользователями (CRUD + события)
- **health-service** - метрики здоровья, активности, рекомендации
- **nutrition-service** - питание, продукты (интеграция с OpenFoodFacts)
- **integrations-service** - интеграция с OpenWeather API

### Event-Driven Communication

Сервисы обмениваются событиями через RabbitMQ (FastStream):

| Событие | Издатель | Подписчики |
|---------|----------|------------|
| `user.created` | users-service | health-service, nutrition-service |
| `user.deleted` | users-service | health-service, nutrition-service |
| `activity.created` | health-service | integrations-service |
| `weather.updated` | integrations-service | health-service |

## Технологии

- **Python 3.11+**
- **FastAPI** 
- **FastStream**
- **RabbitMQ**
- **PostgreSQL** 
- **SQLAlchemy 2.x**
- **Alembic**
- **Docker + docker-compose** 
- **pytest + coverage**

## Запуск

### 1. Настройка окружения

```bash
cp .env.example .env
# Отредактируйте .env, добавьте OPENWEATHER_API_KEY
```

### 2. Запуск всех сервисов

```bash
docker-compose up --build
```

### 3. Доступные эндпоинты

- **API Gateway**: http://localhost:8000
- **Swagger UI**: http://localhost:8000/docs
- **RabbitMQ Management**: http://localhost:15672 (admin/admin123)

### Порты сервисов

| Сервис | Порт |
|--------|------|
| API Gateway | 8000 |
| Users Service | 8001 |
| Health Service | 8002 |
| Nutrition Service | 8003 |
| Integrations Service | 8004 |
| PostgreSQL | 5432 |
| RabbitMQ | 5672 (AMQP), 15672 (Management) |

## 📊 Сущности (4 таблицы)

1. **Users** - пользователи системы
2. **HealthMetrics** - метрики здоровья (шаги, калории, пульс, сон)
3. **Activities** - физическая активность
4. **Foods** - продукты питания
5. **Meals** - приёмы пищи
6. **WeatherLogs** - логи погоды
7. **Recommendations** - рекомендации

## Структура проекта

```
healthhub/
├── services/
│   ├── api-gateway/           # API Gateway
│   │   ├── infrastructure/
│   │   │   ├── auth.py        # JWT authentication
│   │   │   ├── http_client.py # HTTP client for services
│   │   │   ├── messaging.py   # RabbitMQ publisher
│   │   │   └── settings.py
│   │   ├── presentation/
│   │   │   ├── routers.py     # API routes
│   │   │   ├── schemas.py     # Pydantic models
│   │   │   └── dependencies.py
│   │   └── main.py
│   │
│   ├── users-service/         # Users microservice
│   │   ├── domain/
│   │   │   ├── entities.py    # Domain entities
│   │   │   ├── repositories.py # Repository interfaces
│   │   │   └── use_cases.py   # Business logic
│   │   ├── infrastructure/
│   │   │   ├── database.py
│   │   │   ├── models.py      # SQLAlchemy models
│   │   │   ├── repositories.py # Repository implementations
│   │   │   ├── messaging.py   # Event publisher
│   │   │   └── settings.py
│   │   ├── application/
│   │   │   └── services.py    # Application services
│   │   ├── presentation/
│   │   │   ├── routers.py
│   │   │   └── schemas.py
│   │   ├── alembic/           # Migrations
│   │   └── main.py
│   │
│   ├── health-service/        # Health microservice
│   │   ├── domain/
│   │   ├── infrastructure/
│   │   │   ├── messaging.py   # Event publisher
│   │   │   └── consumers.py   # Event consumers
│   │   ├── application/
│   │   ├── presentation/
│   │   ├── main.py            # HTTP API
│   │   └── main_consumer.py   # RabbitMQ consumer
│   │
│   ├── nutrition-service/     # Nutrition microservice
│   │   └── ... (similar structure)
│   │
│   └── integrations-service/  # Integrations microservice
│       └── ... (similar structure)
│
├── shared/                    # Shared modules
│   ├── events.py             # Event schemas
│   └── broker.py             # Broker utilities
│
├── tests/
│   ├── test_users_service.py
│   ├── test_health_service.py
│   ├── test_nutrition_service.py
│   ├── test_integrations_service.py
│   └── test_messaging.py
│
├── docker-compose.yml
├── Makefile
├── pyproject.toml
├── pytest.ini
└── README.md
```

## Тестирование


```bash
pytest --cov=services --cov-report=term-missing --cov-report=html
```

