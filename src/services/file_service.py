import os
from pathlib import Path
from urllib.parse import unquote

from src.core.exceptions import FileNotFoundError


class FileService:
    def get_metadata(self, file_path: str) -> dict:
        """Get metadata for a file"""
        decoded_path = unquote(file_path)
        path = Path(decoded_path)

        if not path.exists():
            raise FileNotFoundError(f"File not found: {decoded_path}")

        if not os.access(path, os.R_OK):
            raise PermissionError(f"Cannot read file: {decoded_path}")

        stats = path.stat()
        return {
            "name": path.name,
            "size": stats.st_size,
            "created": stats.st_ctime,
            "modified": stats.st_mtime,
            "is_file": path.is_file(),
            "is_dir": path.is_dir(),
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

    def list_directory(self, dir_path: str) -> list[dict]:
        """List contents of a directory"""
        decoded_path = unquote(dir_path)
        path = Path(decoded_path)

        if not path.exists():
            raise FileNotFoundError(f"Directory not found: {decoded_path}")

        if not path.is_dir():
            raise NotADirectoryError(f"Path is not a directory: {decoded_path}")

        if not os.access(path, os.R_OK):
            raise PermissionError(f"Cannot read directory: {decoded_path}")

        contents = []
        for item in path.iterdir():
            stats = item.stat()
            contents.append(
                {
                    "name": item.name,
                    "size": stats.st_size,
                    "created": stats.st_ctime,
                    "modified": stats.st_mtime,
                    "is_dir": item.is_dir(),
                    "is_file": item.is_file(),
                }
            )

        return contents
