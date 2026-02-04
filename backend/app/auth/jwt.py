from datetime import datetime, timedelta
from jose import jwt 
from app.core.config import settings

def create_access_token(user_id: str):

    payload = {
        "sub": str(user_id),
        "exp": datetime.datetime.now(datetime.UTC) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    }



