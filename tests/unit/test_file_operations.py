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
    test_dir.mkdir(parents=True)

    # Request directory contents
    response = client.get(
        "/api/v1/files/list",
        params={"path": "", "base_path": str(test_dir)},  # Pass base_path as parameter
        headers=auth_headers,
    )

    # Verify response
    assert response.status_code == 200
    data = response.json()
    assert "contents" in data
    assert len(data["contents"]) == 0
