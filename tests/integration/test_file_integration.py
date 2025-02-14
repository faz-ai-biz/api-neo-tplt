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


def test_directory_tree_traversal(client, auth_headers, tmp_path):
    """
    DIR-002: Validate directory tree traversal functionality

    Expected:
    - Response status code is 200 OK
    - Response correctly represents nested directory structure
    - All files and subdirectories are included in the response
    - Metadata for each item is complete and accurate
    """
    # Create a nested directory structure
    dir1 = tmp_path / "dir1"
    dir1.mkdir()
    dir2 = dir1 / "dir2"
    dir2.mkdir()

    # Create some files in different directories
    (tmp_path / "root_file.txt").write_text("root content")
    (dir1 / "file1.txt").write_text("dir1 content")
    (dir2 / "file2.txt").write_text("dir2 content")

    # Test root directory listing
    response = client.get(
        "/api/v1/files/list",
        params={"path": "", "base_path": str(tmp_path)},
        headers=auth_headers,
    )

    # Verify root response
    assert response.status_code == 200
    root_data = response.json()
    assert "contents" in root_data
    root_contents = root_data["contents"]

    # Verify root level contents
    assert len(root_contents) == 2  # dir1 and root_file.txt

    # Find dir1 in contents
    dir1_entry = next(
        (item for item in root_contents if item["is_dir"] and "dir1" in item["path"]),
        None,
    )
    assert dir1_entry is not None, "dir1 not found in root contents"

    # Test subdirectory listing (dir1)
    response = client.get(
        "/api/v1/files/list",
        params={"path": "dir1", "base_path": str(tmp_path)},
        headers=auth_headers,
    )

    # Verify dir1 response
    assert response.status_code == 200
    dir1_data = response.json()
    assert "contents" in dir1_data
    dir1_contents = dir1_data["contents"]

    # Verify dir1 contents
    assert len(dir1_contents) == 2  # dir2 and file1.txt

    # Test deepest directory (dir2)
    response = client.get(
        "/api/v1/files/list",
        params={"path": "dir1/dir2", "base_path": str(tmp_path)},
        headers=auth_headers,
    )

    # Verify dir2 response
    assert response.status_code == 200
    dir2_data = response.json()
    assert "contents" in dir2_data
    dir2_contents = dir2_data["contents"]

    # Verify dir2 contents
    assert len(dir2_contents) == 1  # just file2.txt

    # Verify metadata for a file in the deepest directory
    file2_entry = dir2_contents[0]
    assert file2_entry["is_file"]
    assert "file2.txt" in file2_entry["path"]
    assert "size" in file2_entry
    assert "last_modified" in file2_entry
