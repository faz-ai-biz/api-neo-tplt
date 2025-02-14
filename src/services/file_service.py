import hashlib
import mimetypes
import os
from datetime import datetime
from pathlib import Path
from urllib.parse import quote, unquote

from src.core.exceptions import FileNotFoundError

class FileService:
    def get_metadata(self, file_path: str) -> dict:
        """Get metadata for a file"""
        # Decode any URL-encoded characters in the path
        decoded_path = unquote(file_path)
        path = Path(decoded_path)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {decoded_path}")
            
        if not os.access(path, os.R_OK):
            raise PermissionError(f"Cannot read file: {decoded_path}")
            
        stats = path.stat()
        
        # Calculate SHA-256 checksum
        sha256_hash = hashlib.sha256()
        with open(path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
                
        return {
            "name": path.name,
            "path": str(path),
            "size": stats.st_size,
            "mimeType": mimetypes.guess_type(path)[0] or "application/octet-stream",
            "modified": datetime.fromtimestamp(stats.st_mtime).isoformat(),
            "created": datetime.fromtimestamp(stats.st_ctime).isoformat(),
            "checksum": sha256_hash.hexdigest(),
            "permissions": {
                "readable": os.access(path, os.R_OK)
            }
        } 