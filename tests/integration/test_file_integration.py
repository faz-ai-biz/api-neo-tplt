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

    # Request file content
    response = client.get(
        "/api/v1/files/content", params={"path": str(test_file)}, headers=headers
    )

    # Verify successful response
    assert response.status_code == 200
    response_data = response.json()
    assert "content" in response_data
    assert response_data["content"] == test_content


def test_zero_byte_file(client, tmp_path):
    """
    Test ID: FILE-008
    Category: File Operations
    Description: Zero byte file
    Expected Result: 200 OK with empty content
    Type: Integration
    """
    # Create an empty file
    test_file = tmp_path / "empty.txt"
    test_file.touch()  # Creates a zero-byte file

    # Get valid token with correct scope
    token = create_test_token(scopes=["files:read"])
    headers = {"Authorization": f"Bearer {token}"}

    # Request file content
    response = client.get(
        "/api/v1/files/content", params={"path": str(test_file)}, headers=headers
    )

    # Verify successful response with empty content
    assert response.status_code == 200
    response_data = response.json()
    assert "content" in response_data
    assert response_data["content"] == ""
