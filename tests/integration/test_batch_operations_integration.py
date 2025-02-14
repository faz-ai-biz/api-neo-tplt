import pytest
from fastapi.testclient import TestClient

from src.main import app  # Adjust the import if your app entry point is different

client = TestClient(app)


def test_batch_multiple_valid_files(client, auth_headers, tmp_path):
    """
    BATCH-001: Validate that multiple valid file paths return the correct metadata
    for each provided file.

    Expected:
    - Response status code is 200 OK.
    - The response returns a JSON array containing metadata for each file.
    """
    # Create test files
    test_files = ["file1.txt", "file2.txt", "image.png"]
    for filename in test_files:
        test_file = tmp_path / filename
        test_file.write_text("Test content")

    payload = {"paths": test_files}

    # Use the auth_headers fixture instead of hardcoded token
    headers = {**auth_headers, "Content-Type": "application/json"}

    response = client.post(
        "/api/v1/files/batch",
        json=payload,
        headers=headers,
        params={"base_path": str(tmp_path)},
    )

    # Validate the response status code
    assert (
        response.status_code == 200
    ), f"Expected status code 200, got {response.status_code}"

    # Validate the response structure
    data = response.json()
    assert isinstance(data, list), "Expected response to be a list of metadata objects"
    assert len(data) == len(
        payload["paths"]
    ), f"Expected metadata for {len(payload['paths'])} files, got {len(data)}"

    # Optionally, validate that each metadata object contains expected keys.
    for item in data:
        # Adjust the key names based on your API's response structure
        assert "path" in item, "Metadata must include 'path'"
        assert "size" in item, "Metadata must include 'size'"
        assert "last_modified" in item, "Metadata must include 'last_modified'"
