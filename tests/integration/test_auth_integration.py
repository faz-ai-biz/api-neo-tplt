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


def test_tampered_signature(client, tmp_path):
    """
    Test ID: AUTH-008
    Category: Authentication
    Description: Tampered JWT signature
    Expected Result: 401 Unauthorized with AUTH002 code
    Type: Security
    """
    # Create a test file
    test_file = tmp_path / "test.txt"
    test_file.write_text("Test content")

    # Create valid token first
    token = create_test_token(scopes=["files:read"])

    # Tamper with the signature (last part after the last dot)
    parts = token.rsplit(".", 1)
    tampered_token = parts[0] + ".tampered_signature"

    headers = {"Authorization": f"Bearer {tampered_token}"}

    # Request file metadata with tampered token
    response = client.get(
        "/api/v1/files", params={"path": str(test_file)}, headers=headers
    )

    # Verify unauthorized access
    assert response.status_code == 401
    error_response = response.json()
    assert "error" in error_response
    assert error_response["error"]["code"] == "AUTH002"
    assert any(
        msg in error_response["error"]["message"].lower()
        for msg in [
            "invalid signature",
            "signature verification failed",
            "invalid token",
        ]
    )
