from abc import ABC, abstractmethod
from typing import Any, Dict, List


class StorageBackend(ABC):
    @abstractmethod
    def get_metadata(self, path: str) -> Dict[str, Any]:
        pass

    @abstractmethod
    def read_content(self, path: str) -> str:
        pass

    @abstractmethod
    def list_items(self, path: str) -> List[str]:
        pass
