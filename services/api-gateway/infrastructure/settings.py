from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    service_port: int = 8000
    users_service_url: str = "http://localhost:8001"
    health_service_url: str = "http://localhost:8002"
    nutrition_service_url: str = "http://localhost:8003"
    integrations_service_url: str = "http://localhost:8004"
    rabbitmq_url: str = "amqp://admin:admin123@localhost:5672/"
    jwt_secret_key: str = "your-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()



