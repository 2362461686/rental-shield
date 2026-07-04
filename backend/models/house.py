"""房源相关 Pydantic schemas"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class HouseSummary(BaseModel):
    """房源列表卡片数据"""
    id: int
    title: str
    district: str
    community: str
    layout: str
    area: float
    price: int
    orientation: str
    floor: int
    total_floors: int
    sunlight_hours: float
    sunlight_level: str
    noise_db: float
    noise_level: str
    risk_score: int
    risk_label: str
    primary_image_url: Optional[str] = None
    review_count: int = 0
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    commute_duration: Optional[int] = None
    commute_score: Optional[float] = None

    model_config = {"from_attributes": True}


class HouseDetail(BaseModel):
    """房源详情全量数据"""
    id: int
    title: str
    district: str
    community: str
    layout: str
    area: float
    price: int
    floor: int
    total_floors: int
    orientation: str
    window_type: str
    building_type: str
    building_year: int
    distance_to_street: int
    has_business_below: bool
    landlord_phone_hash: Optional[str] = None
    source_url: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    created_at: Optional[datetime] = None

    # 预计算字段
    sunlight_hours: float
    sunlight_level: str
    noise_db: float
    noise_level: str
    market_price: int
    price_deviation: float
    is_price_reasonable: bool

    model_config = {"from_attributes": True}


class HouseFilter(BaseModel):
    """搜索筛选参数"""
    districts: Optional[list[str]] = None
    layout: Optional[str] = None
    min_price: int = Field(default=0, ge=0)
    max_price: int = Field(default=8000, le=99999)
    sort_by: str = Field(default="综合推荐")
    keyword: Optional[str] = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=50, ge=1, le=100)


class ReviewResponse(BaseModel):
    """评论响应"""
    id: int
    platform: str
    content: str
    rating: int
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class PriceHistoryResponse(BaseModel):
    """价格历史响应"""
    id: int
    price: int
    record_date: Optional[datetime] = None

    model_config = {"from_attributes": True}


class ImageResponse(BaseModel):
    """图片响应"""
    id: int
    image_path: str
    is_primary: bool
    sort_order: int

    model_config = {"from_attributes": True}


class DistrictRiskBreakdown(BaseModel):
    """区域风险分布"""
    low: int = 0
    medium: int = 0
    high: int = 0


class DistrictStats(BaseModel):
    """区域统计信息"""
    district: str
    house_count: int
    avg_price: float
    min_price: int
    max_price: int
    avg_sunlight: float
    avg_noise: float
    risk_breakdown: DistrictRiskBreakdown = DistrictRiskBreakdown()


class DistrictComparison(BaseModel):
    """多区域对比数据"""
    districts: list[DistrictStats] = []
    total_houses: int = 0
    avg_price_all: float = 0
