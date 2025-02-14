import uuid
from datetime import datetime
from typing import Any, Optional


def create_error_response(
    code: str, message: str, status_code: int, details: Optional[Any] = None
) -> dict:
    """
    Create a standardized error response
    """
    return {
        "error": {
            "code": code,
            "message": message,
            "details": details,
            "requestId": str(uuid.uuid4()),
            "timestamp": datetime.utcnow().isoformat(),
        }
    }
