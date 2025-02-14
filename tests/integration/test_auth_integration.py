import uuid
from datetime import datetime
from pathlib import Path

import pytest

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
