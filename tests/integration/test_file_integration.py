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


def test_directory_pagination(client, auth_headers, tmp_path):
    """
    DIR-003: Validate directory listing pagination functionality

    Expected:
    - Response includes pagination metadata (cursor, has_more)
    - Respects the limit parameter
    - Returns correct items for each page
    - Handles cursor-based navigation correctly
    """
    # Create test files (more than default limit)
    num_files = 75  # Create enough files to span multiple pages
    for i in range(num_files):
        test_file = tmp_path / f"file_{i:03d}.txt"
        test_file.write_text(f"Content for file {i}")

    # Test first page with custom limit
    limit = 30
    response = client.get(
        "/api/v1/files/list",
        params={"path": "", "base_path": str(tmp_path), "limit": limit},
        headers=auth_headers,
    )

    # Verify first page response
    assert response.status_code == 200
    data = response.json()
    assert "contents" in data
    assert "pagination" in data
    assert "cursor" in data["pagination"]
    assert "has_more" in data["pagination"]

    # Verify first page contents
    first_page = data["contents"]
    assert len(first_page) == limit
    first_cursor = data["pagination"]["cursor"]
    assert data["pagination"]["has_more"] is True

    # Get second page using cursor
    response = client.get(
        "/api/v1/files/list",
        params={
            "path": "",
            "base_path": str(tmp_path),
            "limit": limit,
            "cursor": first_cursor,
        },
        headers=auth_headers,
    )

    # Verify second page response
    assert response.status_code == 200
    data = response.json()
    second_page = data["contents"]
    assert len(second_page) == limit
    second_cursor = data["pagination"]["cursor"]
    assert data["pagination"]["has_more"] is True

    # Verify no duplicate items between pages
    first_page_paths = {item["path"] for item in first_page}
    second_page_paths = {item["path"] for item in second_page}
    assert not (
        first_page_paths & second_page_paths
    ), "Found duplicate items between pages"

    # Get final page
    response = client.get(
        "/api/v1/files/list",
        params={
            "path": "",
            "base_path": str(tmp_path),
            "limit": limit,
            "cursor": second_cursor,
        },
        headers=auth_headers,
    )

    # Verify final page response
    assert response.status_code == 200
    data = response.json()
    final_page = data["contents"]
    expected_final_count = num_files - (2 * limit)  # Remaining files
    assert len(final_page) == expected_final_count
    assert data["pagination"]["has_more"] is False

    # Verify total number of items received matches created files
    total_items = len(first_page) + len(second_page) + len(final_page)
    assert total_items == num_files

    # Test invalid cursor
    response = client.get(
        "/api/v1/files/list",
        params={"path": "", "base_path": str(tmp_path), "cursor": "invalid_cursor"},
        headers=auth_headers,
    )
    assert response.status_code == 400

    # Test out of range limit
    response = client.get(
        "/api/v1/files/list",
        params={
            "path": "",
            "base_path": str(tmp_path),
            "limit": 201,  # Spec mentions max limit of 200
        },
        headers=auth_headers,
    )
    assert response.status_code == 422  # FastAPI returns 422 for validation errors
    error_detail = response.json()
    assert "detail" in error_detail  # Verify error details are included
