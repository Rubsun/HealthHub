from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    rabbitmq_url: str
    service_port: int = 8003
    openfoodfacts_api_url: str = "https://world.openfoodfacts.org/api/v2"

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()



