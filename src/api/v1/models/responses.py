from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel


class FileMetadataResponse(BaseModel):
    """Response model for file metadata"""

    path: str
    size: int
    created: float
    last_modified: float
    is_file: bool
    is_dir: bool


class PaginationInfo(BaseModel):
    """Pagination information"""

    cursor: Optional[str] = None
    has_more: bool = False


class PaginatedDirectoryResponse(BaseModel):
    """Response model for paginated directory listing"""

    contents: List[FileMetadataResponse]
    pagination: PaginationInfo


class ErrorResponse(BaseModel):
    """Standard error response model"""

    error: Dict[str, Optional[str]]
