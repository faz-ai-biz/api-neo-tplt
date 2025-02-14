from pathlib import Path

import pytest
from fastapi.testclient import TestClient


def test_get_nonexistent_file_metadata(client, auth_headers):
    """
    Test ID: FILE-004
    Category: Edge Case
    Description: Get metadata for non-existent file
    Expected Result: 404 Not Found, FILE001 code
    Type: Unit
    """
    # Request metadata for non-existent file
    nonexistent_path = "/tmp/definitely_does_not_exist.txt"
    response = client.get(
        "/api/v1/files", params={"path": nonexistent_path}, headers=auth_headers
    )

    # Verify response status and error format
    assert response.status_code == 404

    error_response = response.json()
    assert "error" in error_response
    assert error_response["error"]["code"] == "FILE001"
    assert "File not found" in error_response["error"]["message"]
    assert "timestamp" in error_response["error"]
    assert "requestId" in error_response["error"]
