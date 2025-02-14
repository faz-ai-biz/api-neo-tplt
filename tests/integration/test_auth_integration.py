def test_missing_authorization_header(client):
    """
    Test ID: AUTH-005
    Category: Edge Case
    Description: Missing Authorization header
    Expected Result: 401 Unauthorized
    Type: Integration
    """
    # Make request without Authorization header
    response = client.get("/api/v1/files", params={"path": "test.txt"})
    
    assert response.status_code == 401
    
    error_response = response.json()
    assert "error" in error_response
    assert error_response["error"]["code"] == "AUTH001"
    assert "timestamp" in error_response["error"]
    assert "requestId" in error_response["error"]
    assert "message" in error_response["error"]
