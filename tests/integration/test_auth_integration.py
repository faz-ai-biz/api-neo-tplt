from pathlib import Path

import pytest

from tests.conftest import create_test_token


def test_token_with_correct_scope(client, tmp_path):
    """
    Test ID: AUTH-002
    Category: Authentication
    Description: Token with correct scope
    Expected Result: 200 OK
    Type: Integration
    """
    # Create a test file
    test_file = tmp_path / "test.txt"
    test_file.write_text("Test content")

    # Create token with files:read scope
    token = create_test_token(scopes=["files:read"])
    headers = {"Authorization": f"Bearer {token}"}

    # Request file metadata with correctly scoped token
    response = client.get(
        "/api/v1/files",
        params={"path": str(test_file)},  # Use the actual test file path
        headers=headers,
    )

    # Verify successful access
    assert response.status_code == 200
    data = response.json()
    assert "metadata" in data
    assert data["metadata"]["name"] == test_file.name
    assert data["metadata"]["size"] == len("Test content")


def test_missing_authorization_header(client):
    """
    Test ID: AUTH-005
    Category: Edge Case
    Description: Missing Authorization header
    Expected Result: 401 Unauthorized
    Type: Integration
    """
    # Make request without Authorization header
    response = client.get("/api/v1/files", params={"path": "test.txt"})

    assert response.status_code == 401
    error_response = response.json()
    assert "error" in error_response
    assert error_response["error"]["code"] == "AUTH001"
    assert "timestamp" in error_response["error"]
    assert "requestId" in error_response["error"]
    assert "message" in error_response["error"]
