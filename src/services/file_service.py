import os
from base64 import b64decode, b64encode
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import unquote

from src.api.v1.models.responses import (
    FileMetadataResponse,
    PaginatedDirectoryResponse,
    PaginationInfo,
)
from src.core.exceptions import FileNotFoundError
from src.core.interfaces.storage import StorageBackend
from src.infrastructure.storage.filesystem import FilesystemStorage


class FileService:
    def __init__(self, storage: FilesystemStorage):
        self.storage = storage

    # Helper method to resolve a relative path using the base_path
    def _resolve_path(self, path: str) -> Path:
        return self.base_path / path if path else self.base_path

    def get_metadata(self, path: str) -> Dict[str, Any]:
        """Get metadata for a file or directory"""
        return self.storage.get_metadata(path)

    def get_content(self, path: str) -> str:
        full_path = self._resolve_path(path)
        if not full_path.is_file():
            raise FileNotFoundError(f"File {path} not found")
        return full_path.read_text()

    def list_directory(
        self, path: str, limit: Optional[int] = None, cursor: Optional[str] = None
    ) -> Dict[str, Any]:
        """List contents of a directory with pagination"""
        items = self.storage.list_items(path)

        # Handle pagination
        start_idx = 0
        if cursor:
            try:
                start_idx = int(cursor)
            except ValueError:
                raise ValueError("Invalid cursor format")

        if limit:
            end_idx = start_idx + limit
            has_more = end_idx < len(items)
            items = items[start_idx:end_idx]
        else:
            has_more = False

        # Get metadata for each item
        contents = []
        for item_path in items:
            try:
                metadata = self.get_metadata(item_path)
                contents.append(metadata)
            except FileNotFoundError:
                continue

        return {
            "contents": contents,
            "pagination": {
                "cursor": str(start_idx + len(contents)) if has_more else None,
                "has_more": has_more,
            },
        }

    def read_file_content(self, file_path: str) -> str:
        """Read content from a text file"""
        decoded_path = unquote(file_path)
        path = Path(decoded_path)

        if not path.exists():
            raise FileNotFoundError(f"File not found: {decoded_path}")

        if not os.access(path, os.R_OK):
            raise PermissionError(f"Cannot read file: {decoded_path}")

        try:
            return path.read_text()
        except UnicodeDecodeError:
            raise UnicodeDecodeError(
                "utf-8", b"", 0, 1, "File is not a valid text file"
            )
