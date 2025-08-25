from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    REDIS_URL: str
    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str
    SESSION_SECRET: str
    CBR_URL: str = "https://www.cbr-xml-daily.ru/daily_json.js"
    EXRATE_TTL_SECONDS: int = 3600

    class Config:
        env_file = ".env"

settings = Settings()