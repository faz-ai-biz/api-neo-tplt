import time

import jwt

from src.core.config import settings
from tests.conftest import create_test_token


def test_insufficient_scope(client, tmp_path):
    """
    Test ID: AUTH-007
    Category: Authentication
    Description: Token with insufficient scope
    Expected Result: 403 Forbidden, AUTH004 code
    Type: Integration
    """
    # Create a test file
    test_file = tmp_path / "test.txt"
    test_file.write_text("Test content")

    # Create token with insufficient scope
    token = create_test_token(scopes=["profile:read"])  # Wrong scope
    headers = {"Authorization": f"Bearer {token}"}

    # Request file metadata with insufficient scope
    response = client.get(
        "/api/v1/files", params={"path": str(test_file)}, headers=headers
    )

    # Verify forbidden access
    assert response.status_code == 403
    error_response = response.json()
    assert "error" in error_response
    assert error_response["error"]["code"] == "AUTH004"
    assert "Token missing required scope" in error_response["error"]["message"]


def test_expired_token(client, tmp_path):
    """
    Test ID: AUTH-003
    Category: Authentication
    Description: Expired JWT token
    Expected Result: 401 Unauthorized
    Type: Integration
    """
    # Create a test file
    test_file = tmp_path / "test.txt"
    test_file.write_text("Test content")

    # Create an expired token (exp set to past time)
    payload = {
        "sub": "test_user",
        "exp": int(time.time()) - 3600,  # 1 hour in the past
        "iat": int(time.time()) - 7200,  # 2 hours in the past
        "aud": settings.AUTH_TOKEN_AUDIENCE,
        "iss": settings.AUTH_TOKEN_ISSUER,
        "scope": ["files:read"],
    }
    expired_token = jwt.encode(
        payload, settings.AUTH_SECRET_KEY, algorithm=settings.AUTH_ALGORITHM
    )
    headers = {"Authorization": f"Bearer {expired_token}"}

    # Request file metadata with expired token
    response = client.get(
        "/api/v1/files", params={"path": str(test_file)}, headers=headers
    )

    # Verify unauthorized access
    assert response.status_code == 401
    error_response = response.json()
    assert "error" in error_response
    assert error_response["error"]["code"] == "AUTH002"
    assert "Token has expired" in error_response["error"]["message"]
