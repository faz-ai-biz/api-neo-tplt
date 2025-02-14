from typing import List

from pydantic import BaseModel


class BatchFileRequest(BaseModel):
    paths: List[str]
