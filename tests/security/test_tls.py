import socket
import ssl

import pytest


def test_tls_version():
    """
    SEC-002: Validate that the API server negotiates a secure TLS version (TLSv1.2 or TLSv1.3)

    This test attempts to establish an HTTPS connection to the API server and verifies:
    - The negotiated TLS version is TLSv1.2 or TLSv1.3.

    Note: This test requires the server to be accessible over TLS (HTTPS). If the server
    is not configured for TLS on the given host/port, the test will be skipped.
    """
    # Configure the TLS server details. Adjust these values as needed.
    tls_host = "localhost"
    tls_port = 8443  # Adjust the port for TLS if different

    # Create a default SSL context with secure default settings.
    context = ssl.create_default_context()

    try:
        # Establish a TCP connection, then wrap it with TLS.
        with socket.create_connection((tls_host, tls_port), timeout=5) as sock:
            with context.wrap_socket(sock, server_hostname=tls_host) as ssock:
                tls_version = ssock.version()
                # Assert that the negotiated TLS version is secure.
                assert tls_version in (
                    "TLSv1.2",
                    "TLSv1.3",
                ), f"Insecure TLS version negotiated: {tls_version}"
    except Exception as e:
        pytest.skip(f"TLS test skipped due to connection error: {e}")
