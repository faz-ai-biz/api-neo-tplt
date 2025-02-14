from fastapi import APIRouter, Depends, status, HTTPException
from datetime import datetime
import os
from pathlib import Path
import uuid

from src.api.dependencies.auth import verify_token
from src.services.file_service import FileService
from src.core.exceptions import FileNotFoundError

# Create router instance
router = APIRouter(prefix="/files", tags=["files"])

@router.get("")
async def get_file_metadata(
    path: str,
    token_data=Depends(verify_token),
    file_service: FileService = Depends()
):
    """
    Get metadata for a file
    """
    try:
        metadata = file_service.get_metadata(path)
        return {"metadata": metadata}
    except FileNotFoundError as e:
        # Re-raise the custom exception to be handled by our error handler
        raise e
    except PermissionError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to access file"
        ) 