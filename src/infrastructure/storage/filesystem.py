from pathlib import Path
from typing import Any, Dict, List
from urllib.parse import unquote

from src.core.exceptions import FileNotFoundError
from src.core.interfaces.storage import StorageBackend


class FilesystemStorage(StorageBackend):
    def __init__(self, base_path: Path):
        self.base_path = base_path

    def _resolve_path(self, path: str) -> Path:
        decoded_path = unquote(path)
        return self.base_path / decoded_path

    def get_metadata(self, path: str) -> Dict[str, Any]:
        full_path = self._resolve_path(path)
        if not full_path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        stats = full_path.stat()
        return {
            "path": str(full_path),
            "size": stats.st_size,
            "created": stats.st_ctime,
            "last_modified": stats.st_mtime,
            "is_file": full_path.is_file(),
            "is_dir": full_path.is_dir(),
        }

    def read_content(self, path: str) -> str:
        full_path = self._resolve_path(path)
        if not full_path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        return full_path.read_text()

    def list_items(self, path: str) -> List[str]:
        full_path = self._resolve_path(path)
        if not full_path.exists():
            raise FileNotFoundError(f"Directory not found: {path}")
        if not full_path.is_dir():
            raise ValueError(f"Path is not a directory: {path}")
        return [str(p.relative_to(self.base_path)) for p in full_path.iterdir()]
