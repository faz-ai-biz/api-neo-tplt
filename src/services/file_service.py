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

    def list_directory(
        self, path: str = "", limit: int = 50, cursor: str = None
    ) -> Dict[str, Any]:
        """
        List contents of a directory with pagination support

        Args:
            path: Directory path relative to base_path
            limit: Maximum number of items per page
            cursor: Opaque cursor for pagination

        Returns:
            Dict containing:
            - contents: List of file/directory metadata
            - pagination: Dict with cursor and has_more flag
        """
        try:
            full_path = self._resolve_path(path)

            if not full_path.exists():
                raise FileNotFoundError(f"Directory not found: {path}")

            if not full_path.is_dir():
                raise ValueError(f"Not a directory: {path}")

            # Get all items and sort them by name for consistent pagination
            all_items = sorted(full_path.iterdir(), key=lambda x: x.name)

            # Handle cursor-based pagination
            if cursor:
                try:
                    # Cursor format: base64(filename)
                    from base64 import b64decode

                    cursor_name = b64decode(cursor.encode()).decode()
                    # Find the item after the cursor
                    start_idx = next(
                        (
                            i
                            for i, item in enumerate(all_items)
                            if item.name > cursor_name
                        ),
                        len(all_items),
                    )
                    all_items = all_items[start_idx:]
                except Exception:
                    raise ValueError("Invalid cursor format")

            # Get items for current page
            page_items = all_items[:limit]
            has_more = len(all_items) > limit

            # Generate next cursor if there are more items
            next_cursor = None
            if has_more and page_items:
                from base64 import b64encode

                last_name = page_items[-1].name
                next_cursor = b64encode(last_name.encode()).decode()

            # Get metadata for page items
            contents = [
                self.get_metadata(str(item.relative_to(self.base_path)))
                for item in page_items
            ]

            return {
                "contents": contents,
                "pagination": {"cursor": next_cursor, "has_more": has_more},
            }
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
