# src/config.py
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "genvid-backend"
    ENV: str = "development"
    DEBUG: bool = True

    class Config:
        env_file = ".env"
        case_sensitive = False
