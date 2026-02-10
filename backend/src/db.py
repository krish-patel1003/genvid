# src/db.py
from sqlmodel import SQLModel, create_engine, Session
from src.config import get_settings

settings = get_settings()

engine = create_engine(
    settings.DATABASE_URL,
    echo=True,
    pool_pre_ping=True,
)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
