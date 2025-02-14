from typing import Dict

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from src.core.config import settings
from src.core.exceptions import InvalidTokenError
from src.utils.response import create_error_response

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=True)


def verify_token(token: str = Depends(oauth2_scheme)) -> Dict:
    """
    Verify JWT token and return payload if valid
    """
    try:
        payload = jwt.decode(
            token,
            settings.AUTH_SECRET_KEY,
            algorithms=[settings.AUTH_ALGORITHM],
            audience=settings.AUTH_TOKEN_AUDIENCE,
            issuer=settings.AUTH_TOKEN_ISSUER,
        )

        # Verify required scope is present
        scopes = payload.get("scope", [])
        if "files:read" not in scopes:
            error_response = create_error_response(
                code="AUTH004",
                message="Token missing required scope",
                status_code=status.HTTP_403_FORBIDDEN,
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail=error_response
            )

        return payload
    except jwt.ExpiredSignatureError:
        raise InvalidTokenError("Token has expired")
    except jwt.InvalidTokenError as e:
        raise InvalidTokenError(str(e))
