from typing import Dict

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from src.core.config import settings
from src.core.exceptions import InvalidTokenError

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=True)

def verify_token(token: str = Depends(oauth2_scheme)) -> Dict:
    """
    Verify JWT token and return payload if valid
    
    The OAuth2PasswordBearer dependency will automatically raise
    401 Unauthorized when the Authorization header is missing
    """
    try:
        payload = jwt.decode(
            token,
            settings.AUTH_SECRET_KEY,
            algorithms=[settings.AUTH_ALGORITHM],
            audience=settings.AUTH_TOKEN_AUDIENCE,
            issuer=settings.AUTH_TOKEN_ISSUER
        )
        return payload
    except jwt.InvalidTokenError as e:
        raise InvalidTokenError(str(e)) 