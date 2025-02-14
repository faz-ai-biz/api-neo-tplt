def test_special_characters_filename(client, auth_headers, tmp_path):
    """Test handling of filenames with special characters"""
    # Create a test file with special characters in name
    filename = "test@#$%^&.txt"
    test_file = tmp_path / filename
    test_file.write_text("Test content")

    # Request file metadata
    response = client.get(
        "/api/v1/files", params={"path": str(test_file)}, headers=auth_headers
    )

    # Verify successful response
    assert response.status_code == 200
    metadata = response.json()["metadata"]
    assert metadata["name"] == filename
