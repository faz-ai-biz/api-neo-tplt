import pytest

from tests.conftest import create_test_token


def test_get_file_content(client, tmp_path):
    """
    Test ID: FILE-002
    Category: File Operations
    Description: Get text file content
    Expected Result: 200 OK with file content
    Type: Integration
    """
    # Create a test file with known content
    test_content = "Hello, this is a test file content!"
    test_file = tmp_path / "test.txt"
    test_file.write_text(test_content)

    # Get valid token with correct scope
    token = create_test_token(scopes=["files:read"])
    headers = {"Authorization": f"Bearer {token}"}

    # Request file content with base_path
    response = client.get(
        "/api/v1/files/content",
        params={"path": "test.txt", "base_path": str(tmp_path)},
        headers=headers,
    )

    # Verify successful response
    assert response.status_code == 200
    assert response.json()["content"] == test_content
