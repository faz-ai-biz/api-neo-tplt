from datetime import datetime, timedelta

import jwt

from src.core.config import settings


def create_test_token(scopes: list[str]) -> str:
    """Create a JWT token with specified scopes for testing"""
    payload = {
        "sub": "test_user",
        "exp": datetime.utcnow() + timedelta(hours=1),
        "iat": datetime.utcnow(),
        "aud": settings.AUTH_TOKEN_AUDIENCE,
        "iss": settings.AUTH_TOKEN_ISSUER,
        "scope": scopes,
    }

    return jwt.encode(
        payload, settings.AUTH_SECRET_KEY, algorithm=settings.AUTH_ALGORITHM
    )
