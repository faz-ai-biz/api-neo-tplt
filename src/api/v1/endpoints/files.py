from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Query, status

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
    path: str, token_data=Depends(verify_token), file_service: FileService = Depends()
):
    """Get content of a text file"""
    try:
        content = file_service.read_file_content(path)
        return {"content": content}
    except FileNotFoundError as e:
        raise e
    except PermissionError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to access file",
        )
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File is not a valid text file",
        )


@router.get("/list")
async def list_directory(
    path: str = "",
    base_path: str = Query(..., description="Base path for file operations"),
    token_data=Depends(verify_token),
):
    """List contents of a directory"""
    try:
        print(
            f"DEBUG: Listing directory with path: {path}, base_path: {base_path}"
        )  # Debug log
        file_service = FileService(base_path=Path(base_path))
        contents = file_service.list_directory(path)
        print(f"DEBUG: Directory contents: {contents}")  # Debug log
        return {"contents": contents}
    except FileNotFoundError as e:
        print(f"ERROR: Directory not found: {str(e)}")  # Debug log
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionError:
        print(f"ERROR: Permission denied for path: {path}")  # Debug log
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to access directory",
        )
    except ValueError as e:
        print(f"ERROR: Invalid directory request: {str(e)}")  # Debug log
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
