from pydantic_settings import BaseSettings

class Settings(BaseSettings):

    # App
    APP_NAME: str = "GenVid"
    ENV: str = "development"

    # Database
    DATABASE_URL: str = "sqlite:///./test.db"

    # Security
    SECRET_KEY: str
    JWT_SECRET: str 
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day

    # OAuth
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    GOOGLE_REDIRECT_URI: str

    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/1"

    # Google Cloud
    GOOGLE_APPLICATION_CREDENTIALS: str

    class Config:
        case_sensitive = True
        extra="ignore"
    

settings = Settings()

