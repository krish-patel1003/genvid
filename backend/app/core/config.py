from pydantic import BaseSettings

class Settings(BaseSettings):

    # App
    APP_NAME: str = "GenVid"
    ENV: str = "development"

    # Database
    DATABASE_URL: str = "sqlite:///./test.db"

    # Security
    JWT_SECRET: str 
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
    

settings = Settings()

