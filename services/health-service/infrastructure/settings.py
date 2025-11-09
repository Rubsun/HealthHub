from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    rabbitmq_url: str
    service_port: int = 8002
    users_service_url: str = "http://localhost:8001"

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()



