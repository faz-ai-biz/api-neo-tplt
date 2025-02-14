from base64 import b64decode, b64encode
from dataclasses import dataclass
from typing import Any, Callable, Generic, List, TypeVar

T = TypeVar("T")


@dataclass
class PaginationResult(Generic[T]):
    items: List[T]
    cursor: str | None
    has_more: bool


class PaginationService:
    @staticmethod
    def paginate(
        items: List[T],
        limit: int,
        cursor: str | None = None,
        get_key: Callable[[T], str] = lambda x: str(x),
    ) -> PaginationResult[T]:
        if cursor:
            try:
                cursor_key = b64decode(cursor.encode()).decode()
                start_idx = next(
                    (i for i, item in enumerate(items) if get_key(item) > cursor_key),
                    len(items),
                )
                items = items[start_idx:]
            except Exception:
                raise ValueError("Invalid cursor format")

        page_items = items[:limit]
        has_more = len(items) > limit

        next_cursor = None
        if has_more and page_items:
            last_key = get_key(page_items[-1])
            next_cursor = b64encode(last_key.encode()).decode()

        return PaginationResult(items=page_items, cursor=next_cursor, has_more=has_more)
