from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import (  # Added Response import for file content
    JSONResponse,
    Response,
)
from pydantic import BaseModel  # Import for BatchRequest model

from src.api.dependencies.auth import verify_token  # Fix import path
from src.api.v1.models.responses import (
    ErrorResponse,
    FileMetadataResponse,
    PaginatedDirectoryResponse,
)
from src.core.exceptions import FileNotFoundError
from src.infrastructure.storage.filesystem import FilesystemStorage
from src.services.file_service import FileService

router = APIRouter(
    prefix="/files", tags=["files"]
)  # Make sure router is defined at module level


class BatchRequest(BaseModel):
    paths: list[str]


@router.get("", response_model=FileMetadataResponse)
async def get_file_metadata(
    path: str,
    base_path: str = Query(..., description="Base path for file operations"),
    token_data=Depends(verify_token),
):
    """Get metadata for a file"""
    try:
        storage = FilesystemStorage(Path(base_path))
        file_service = FileService(storage)
        return file_service.get_metadata(path)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail={"error": {"message": str(e)}})
    except PermissionError:
        raise HTTPException(
            status_code=403, detail={"error": {"message": "Permission denied"}}
        )


@router.get("/content")
async def get_file_content(
    path: str,
    base_path: str = Query(..., description="Base path for file operations"),
    token_data=Depends(verify_token),
):
    """Get content of a text file"""
    try:
        storage = FilesystemStorage(Path(base_path))
        file_service = FileService(storage)
        content = file_service.storage.read_content(path)
        return JSONResponse(content={"content": content})
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail={"error": {"message": str(e)}}
        )
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": {"message": "File is not a valid text file"}},
        )


@router.get("/list", response_model=PaginatedDirectoryResponse)
async def list_directory(
    path: str = "",
    base_path: str = Query(..., description="Base path for file operations"),
    limit: int = Query(50, ge=1, le=200),
    cursor: Optional[str] = None,
    token_data=Depends(verify_token),
):
    """List contents of a directory with pagination"""
    try:
        storage = FilesystemStorage(Path(base_path))
        file_service = FileService(storage)
        return file_service.list_directory(path, limit=limit, cursor=cursor)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": {"message": str(e)}},
        )
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail={"error": {"message": str(e)}}
        )


@router.post("/batch", response_model=list[FileMetadataResponse])
async def batch_get_files(
    payload: BatchRequest,
    base_path: str = Query(..., description="Base path for file operations"),
    token_data=Depends(verify_token),
):
    """Return metadata for multiple files"""
    storage = FilesystemStorage(Path(base_path))
    file_service = FileService(storage)
    results = []
    for file_path in payload.paths:
        try:
            meta = file_service.get_metadata(file_path)
            results.append(meta)
        except FileNotFoundError as e:
            results.append({"path": file_path, "error": str(e)})
    return results
