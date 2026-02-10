from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
import logging

from src.security import decode_token

security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    logger = logging.getLogger(__name__)
    
    token = credentials.credentials

    try:
        payload = decode_token(token)
        logger.info(f"Authenticated user: {payload.get('sub')}")
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    return {
        "user_id": payload.get("sub"),
        "issued_at": payload.get("iat"),
        "expires_at": payload.get("exp"),
    }