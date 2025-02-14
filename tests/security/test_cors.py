import pytest
from fastapi.testclient import TestClient

from src.main import app  # Adjust the import if your app entry point is different

# Create a TestClient instance using our FastAPI app
client = TestClient(app)


def test_cors_allowed_origin_preflight():
    """
    SEC-001: Validate CORS preflight (OPTIONS) response for allowed origin

    Expected:
    - Response status code is 200 (OK)
    - Response headers include 'access-control-allow-origin' with the allowed origin value.
    - Response headers include 'access-control-allow-methods' and 'access-control-allow-headers'
    """
    allowed_origin = (
        "http://localhost:3000"  # as per ENVIROMENT_VARS.md for Test environment
    )
    headers = {
        "Origin": allowed_origin,
        "Access-Control-Request-Method": "GET",
        "Access-Control-Request-Headers": "Authorization",
    }
    response = client.options("/api/v1/system/health", headers=headers)
    assert response.status_code == 200
    # Validate that the CORS header is set with the expected origin
    assert "access-control-allow-origin" in response.headers
    assert response.headers["access-control-allow-origin"] == allowed_origin
    # Validate that allowed methods and headers are provided
    assert "access-control-allow-methods" in response.headers
    assert "access-control-allow-headers" in response.headers


def test_cors_allowed_origin_actual_request():
    """
    SEC-001: Validate that responses include correct CORS headers when 'Origin' header is provided

    Expected:
    - Response includes 'access-control-allow-origin' header matching the allowed origin.
    """
    allowed_origin = "http://localhost:3000"
    headers = {"Origin": allowed_origin}
    response = client.get("/api/v1/system/health", headers=headers)
    # Ensure that the CORS response header exists with the correct value
    assert "access-control-allow-origin" in response.headers
    assert response.headers["access-control-allow-origin"] == allowed_origin
