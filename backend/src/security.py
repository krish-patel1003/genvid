from datetime import datetime, timedelta, timezone
from typing import Dict
import jwt

from src.config import get_settings

def create_access_token(subject: str) -> str:
    settings = get_settings()
    payload: Dict[str, str] = {
        "sub": subject,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_EXP_MINUTES),
        "iat": datetime.now(timezone.utc)
    }
    token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return token


def decode_token(token: str) -> Dict:
    settings = get_settings()
    
    return jwt.decode(
        token,
        settings.JWT_SECRET,
        algorithms=[settings.JWT_ALGORITHM],
    )