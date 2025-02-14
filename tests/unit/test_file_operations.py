def test_special_characters_filename(client, auth_headers, tmp_path):
    """
    Test ID: FILE-007
    Category: Edge Case
    Description: Get metadata for file with special characters in name
    Expected Result: 200 OK with correct metadata
    Type: Unit
    """
    # Create a file with special characters in name
    special_filename = "test!@#$%^&*()_+-=[]{}|;'.txt"
    test_file = tmp_path / special_filename
    test_file.write_text("Test content")

    # Request metadata for file with special characters
    response = client.get(
        "/api/v1/files", params={"path": str(test_file)}, headers=auth_headers
    )

    # Verify response status and metadata
    assert response.status_code == 200
    data = response.json()
    assert "metadata" in data
    assert data["metadata"]["name"] == special_filename
    assert data["metadata"]["path"] == str(test_file)
    assert data["metadata"]["size"] == len("Test content")
