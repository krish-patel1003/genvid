# src/config.py
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    APP_NAME: str = "genvid-backend"
    ENV: str = "development"
    DEBUG: bool = True

    SECRET_KEY: str

    JWT_SECRET: str 
    JWT_ALGORITHM: str 
    JWT_EXP_MINUTES: int 

    DATABASE_URL: str

    SERVICE_URL: str

    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    GCS_BUCKET_NAME: str
    GCP_PROJECT_ID: str
    GCP_PUBSUB_VIDEO_GEN_TOPIC: str

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache
def get_settings() -> Settings:
    return Settings()