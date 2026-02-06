from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):

    # App
    APP_NAME: str = "GenVid API"
    ENV: str = "Production"

    # Database
    DATABASE_URL: str

    # Security
    SECRET_KEY: str
    JWT_SECRET: str 
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day

    # OAuth
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    GOOGLE_REDIRECT_URI: str

    # Celery
    CELERY_BROKER_URL: str 
    CELERY_RESULT_BACKEND: str 

    # Frontend
    FRONTEND_URL: str 

    # ws
    WS_NOTIFY_URL: str

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra="ignore"
    

@lru_cache()
def get_settings() -> Settings:
    return Settings()