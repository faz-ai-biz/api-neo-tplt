from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status

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
    path: str, token_data=Depends(verify_token), file_service: FileService = Depends()
):
    """List contents of a directory"""
    try:
        contents = file_service.list_directory(path)
        return {"contents": contents}
    except FileNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to access directory",
        )
    except NotADirectoryError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Path is not a directory"
        )
