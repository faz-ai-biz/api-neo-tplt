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


def test_list_directory_contents(client, tmp_path):
    """
    Test ID: DIR-001
    Category: File Operations
    Description: List directory contents
    Expected Result: 200 OK with list of files and subdirectories
    Type: Integration
    """
    # Create test directory structure
    test_dir = tmp_path / "test_dir"
    test_dir.mkdir()

    # Create mixed content
    (test_dir / "file1.txt").write_text("content1")
    (test_dir / "file2.txt").write_text("content2")
    subdir = test_dir / "subdir"
    subdir.mkdir()
    (subdir / "subfile.txt").write_text("subcontent")

    # Get valid token with correct scope
    token = create_test_token(scopes=["files:read"])
    headers = {"Authorization": f"Bearer {token}"}

    # Request directory contents
    response = client.get(
        "/api/v1/files/list", params={"path": str(test_dir)}, headers=headers
    )

    # Verify successful response
    assert response.status_code == 200
    contents = response.json()["contents"]

    # Verify directory listing
    assert len(contents) == 3
    assert any(item["name"] == "file1.txt" and not item["is_dir"] for item in contents)
    assert any(item["name"] == "file2.txt" and not item["is_dir"] for item in contents)
    assert any(item["name"] == "subdir" and item["is_dir"] for item in contents)
