import os
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status

from src.api.dependencies.auth import verify_token
from src.core.exceptions import FileNotFoundError
from src.services.file_service import FileService

router = APIRouter(prefix="/files", tags=["files"])


@router.get("")
async def get_file_metadata(
    path: str, token_data=Depends(verify_token), file_service: FileService = Depends()
):
    """
    Get metadata for a file
    """
    try:
        metadata = file_service.get_metadata(path)
        return {"metadata": metadata}  # Ensure we're returning a dict with metadata key
    except FileNotFoundError as e:
        raise e
    except PermissionError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to access file",
        )
