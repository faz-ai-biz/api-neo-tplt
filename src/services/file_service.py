import hashlib
import mimetypes
import os
from datetime import datetime
from pathlib import Path

from src.core.exceptions import FileNotFoundError


class FileService:
    def get_metadata(self, file_path: str) -> dict:
        """Get metadata for a file"""
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
            
        if not os.access(path, os.R_OK):
            raise PermissionError(f"Cannot read file: {file_path}")
            
        # ... rest of the implementation ... 