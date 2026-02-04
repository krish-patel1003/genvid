from typing import Annotated

import jwt
from jwt.exceptions import InvalidTokenError
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.core.config import settings
from app.core.db import SessionLocal
from app.auth.models import User  
from app.core.db import Base, engine


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_db_and_tables():
    Base.metadata.create_all(bind=engine)

def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db=Depends(get_db),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        subject = payload.get("sub")
        if subject is None:
            raise credentials_exception
    except InvalidTokenError:
        raise credentials_exception

    # If your User.id is Integer:
    # user = db.query(User).filter(User.id == int(subject)).first()
    # If your User.id is UUID/String:
    user = db.query(User).filter(User.id == subject).first()

    if not user:
        raise credentials_exception
    return user


def user_exists(user_id: int, db=Depends(get_db)) -> bool:
    user = db.query(User).filter(User.id == user_id).first()
    return user is not None