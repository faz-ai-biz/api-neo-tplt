from typing import Any, Dict, List, Optional

from src.api.v1.models.responses import PaginatedDirectoryResponse, PaginationInfo
from src.core.interfaces.storage import StorageBackend
from src.services.pagination import PaginationService


class FileService:
    def __init__(self, storage: StorageBackend):
        self.storage = storage
        self.pagination = PaginationService()

    def get_metadata(self, path: str) -> Dict[str, Any]:
        """Get metadata for a file or directory"""
        return self.storage.get_metadata(path)

    def read_content(self, path: str) -> str:
        """Read content from a text file"""
        return self.storage.read_content(path)

    def list_directory(
        self, path: str, limit: int = 50, cursor: Optional[str] = None
    ) -> PaginatedDirectoryResponse:
        items = self.storage.list_items(path)
        sorted_items = sorted(items)

        pagination_result = self.pagination.paginate(
            items=sorted_items, limit=limit, cursor=cursor
        )

        contents = [self.get_metadata(item) for item in pagination_result.items]

        return PaginatedDirectoryResponse(
            contents=contents,
            pagination=PaginationInfo(
                cursor=pagination_result.cursor, has_more=pagination_result.has_more
            ),
        )
