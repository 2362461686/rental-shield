"""新建评估的 Pydantic 请求/响应模型"""
from typing import Optional
from pydantic import BaseModel


class ReviewItem(BaseModel):
    """单条评价"""
    platform: str = "user_input"
    content: str = ""


class AssessmentRequest(BaseModel):
    """POST /api/v1/assessments 请求体"""
    title: Optional[str] = None
    source_url: Optional[str] = None
    community: Optional[str] = None
    district: Optional[str] = None
    price: Optional[int] = None
    layout: Optional[str] = None
    area: Optional[float] = None
    floor: Optional[int] = None
    total_floors: Optional[int] = None
    orientation: Optional[str] = None
    distance_to_street: Optional[int] = None
    has_business_below: Optional[bool] = None
    commute_destination: Optional[str] = None
    reviews: Optional[list[ReviewItem]] = None
