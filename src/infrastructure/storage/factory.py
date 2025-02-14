from pathlib import Path

from fastapi import Depends

from src.core.interfaces.storage import StorageBackend
from src.infrastructure.storage.filesystem import FilesystemStorage


def get_storage(base_path: str) -> StorageBackend:
    return FilesystemStorage(Path(base_path))
