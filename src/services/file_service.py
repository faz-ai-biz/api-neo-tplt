import os
from pathlib import Path
from typing import Any, Dict, List
from urllib.parse import unquote

from src.core.exceptions import FileNotFoundError


class FileService:
    def __init__(self, base_path: Path):
        """Initialize FileService with a base path"""
        self.base_path = base_path

    def _resolve_path(self, path: str) -> Path:
        """Resolve and validate a path"""
        try:
            # Decode URL-encoded path
            decoded_path = unquote(path)

            # Resolve the full path
            requested_path = (self.base_path / decoded_path).resolve()

            # Check if the resolved path is within base directory
            if not str(requested_path).startswith(str(self.base_path)):
                raise ValueError("Path traversal attempt detected")

            return requested_path
        except Exception as e:
            raise ValueError(f"Invalid path: {str(e)}")

    def read_file_content(self, path: str) -> str:
        """Read content from a text file"""
        try:
            full_path = self._resolve_path(path)

            if not full_path.exists():
                raise FileNotFoundError(f"File not found: {path}")

            if not full_path.is_file():
                raise ValueError(f"Not a file: {path}")

            if not os.access(full_path, os.R_OK):
                raise PermissionError(f"Cannot read file: {path}")

            return full_path.read_text()
        except ValueError as e:
            raise ValueError(str(e))

    def list_directory(self, path: str = "") -> List[Dict[str, Any]]:
        """List contents of a directory"""
        try:
            full_path = self._resolve_path(path)

            if not full_path.exists():
                raise FileNotFoundError(f"Directory not found: {path}")

            if not full_path.is_dir():
                raise ValueError(f"Not a directory: {path}")

            contents = []
            for item in full_path.iterdir():
                contents.append(
                    self.get_metadata(str(item.relative_to(self.base_path)))
                )
            return contents
        except ValueError as e:
            raise ValueError(str(e))

    def get_metadata(self, path: str) -> Dict[str, Any]:
        """Get metadata for a file or directory"""
        try:
            full_path = self._resolve_path(path)

            if not full_path.exists():
                raise FileNotFoundError(f"Path not found: {path}")

            stats = full_path.stat()
            return {
                "name": full_path.name,
                "path": str(full_path.relative_to(self.base_path)),
                "size": stats.st_size,
                "created": stats.st_ctime,
                "modified": stats.st_mtime,
                "is_file": full_path.is_file(),
                "is_dir": full_path.is_dir(),
            }
        except ValueError as e:
            raise ValueError(str(e))
