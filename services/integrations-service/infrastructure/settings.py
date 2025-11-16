from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    rabbitmq_url: str
    service_port: int = 8004
    openweather_api_key: str = ""
    openweather_api_url: str = "https://api.openweathermap.org/data/2.5"

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()



