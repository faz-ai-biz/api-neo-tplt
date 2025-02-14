def test_empty_directory(client, auth_headers, tmp_path):
    """
    Test ID: DIR-004
    Category: File Operations
    Description: Empty directory
    Expected Result: 200 OK with empty contents list
    Type: Unit
    """
    # Create an empty directory
    test_dir = tmp_path / "empty_dir"
    test_dir.mkdir()

    # Request directory contents
    response = client.get(
        "/api/v1/files/list", params={"path": str(test_dir)}, headers=auth_headers
    )

    # Verify successful response with empty contents
    assert response.status_code == 200
    contents = response.json()["contents"]
    assert isinstance(contents, list)
    assert len(contents) == 0
