import os
from pathlib import Path
from typing import Any, Dict, List
from urllib.parse import unquote

from src.core.exceptions import FileNotFoundError


class FileService:
    def __init__(self, base_path: Path = None):
        if base_path is None:
            base_path = Path.cwd()  # Default to the current working directory
        self.base_path = base_path

    # Helper method to resolve a relative path using the base_path
    def _resolve_path(self, path: str) -> Path:
        return self.base_path / path if path else self.base_path

    def get_metadata(self, file_path: str) -> dict:
        """Get metadata for a file"""
        decoded_path = unquote(file_path)
        full_path = self.base_path / decoded_path

        if not full_path.exists():
            raise FileNotFoundError(f"File not found: {decoded_path}")

        if not os.access(full_path, os.R_OK):
            raise PermissionError(f"Cannot read file: {decoded_path}")

        stats = full_path.stat()
        return {
            "path": str(full_path),
            "size": stats.st_size,
            "created": stats.st_ctime,
            "last_modified": stats.st_mtime,
            "is_file": full_path.is_file(),
            "is_dir": full_path.is_dir(),
        }

    def get_content(self, path: str) -> str:
        full_path = self.base_path / path
        if not full_path.is_file():
            raise FileNotFoundError(f"File {path} not found")
        return full_path.read_text()

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

            return contents  # Return empty list if no contents
        except Exception as e:
            raise ValueError(str(e))

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
