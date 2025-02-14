from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import (  # Added Response import for file content
    JSONResponse,
    Response,
)
from pydantic import BaseModel  # Import for BatchRequest model

from src.api.dependencies.auth import verify_token  # Fix import path
from src.core.exceptions import FileNotFoundError
from src.services.file_service import FileService

router = APIRouter(
    prefix="/files", tags=["files"]
)  # Make sure router is defined at module level


@router.get("")
async def get_file_metadata(
    path: str, token_data=Depends(verify_token), file_service: FileService = Depends()
):
    """Get metadata for a file"""
    try:
        metadata = file_service.get_metadata(path)
        return {"metadata": metadata}
    except FileNotFoundError as e:
        raise e
    except PermissionError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to access file",
        )


@router.get("/content")
async def get_file_content(
    path: str,
    base_path: str = Query(..., description="Base path for file operations"),
    token_data=Depends(verify_token),
):
    """Get content of a text file"""
    try:
        file_service = FileService(base_path=Path(base_path))
        content = file_service.get_content(path)
        return {"content": content}
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/list")
async def list_directory(
    path: str = "",
    base_path: str = Query(..., description="Base path for file operations"),
    token_data=Depends(verify_token),
):
    """List files in a directory"""
    try:
        file_service = FileService(base_path=Path(base_path))
        files = file_service.list_directory(path)
        return {"contents": files}
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


class BatchRequest(BaseModel):
    paths: list[str]


@router.post("/batch")
async def batch_get_files(
    payload: BatchRequest,
    base_path: str = Query(..., description="Base path for file operations"),
    token_data=Depends(verify_token),
):
    """Return metadata for multiple files"""
    file_service = FileService(base_path=Path(base_path))
    results = []
    for file_path in payload.paths:
        try:
            meta = file_service.get_metadata(file_path)
            results.append(meta)
        except FileNotFoundError as e:
            # Append error details per file if not found (alternatively, you could skip or halt)
            results.append({"path": file_path, "error": str(e)})
    return results
