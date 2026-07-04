"""图片相关 Pydantic schemas"""
from pydantic import BaseModel
from typing import Optional


class ScrapeRequest(BaseModel):
    house_ids: Optional[list[int]] = None
    max_per_house: int = 10
    min_per_house: int = 5


class ScrapeStatus(BaseModel):
    job_id: str
    status: str  # running, completed, failed
    progress: int = 0
    total: int = 0
    errors: list[str] = []
