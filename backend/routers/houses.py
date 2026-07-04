"""房源相关 API 路由"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from backend.db.database import get_db
from backend.db import queries
from backend.services import house_service
from backend.models.house import HouseSummary, HouseDetail, ReviewResponse, PriceHistoryResponse, ImageResponse

router = APIRouter(prefix="/api/v1/houses", tags=["houses"])


@router.get("", response_model=list[HouseSummary])
def list_houses(
    districts: Optional[str] = Query(None, description="区域，逗号分隔"),
    layout: Optional[str] = Query(None),
    min_price: int = Query(0),
    max_price: int = Query(8000),
    sort_by: str = Query("综合推荐"),
    keyword: Optional[str] = Query(None, description="关键词搜索（小区名、标题）"),
    db: Session = Depends(get_db),
):
    """房源列表查询，支持筛选和排序"""
    district_list = [d.strip() for d in districts.split(",") if d.strip()] if districts else None
    return house_service.list_houses(db, district_list, layout, min_price, max_price, sort_by, keyword)


@router.get("/{house_id}", response_model=HouseDetail)
def get_house(house_id: int, db: Session = Depends(get_db)):
    """获取房源详情"""
    detail = house_service.get_house_detail(db, house_id)
    if not detail:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="房源不存在")
    return detail


@router.get("/{house_id}/reviews", response_model=list[ReviewResponse])
def get_reviews(house_id: int, db: Session = Depends(get_db)):
    """获取房源所有评论"""
    return queries.get_reviews(db, house_id)


@router.get("/{house_id}/price-history", response_model=list[PriceHistoryResponse])
def get_price_history(house_id: int, db: Session = Depends(get_db)):
    """获取房源价格历史"""
    return queries.get_price_history(db, house_id)


@router.get("/{house_id}/images", response_model=list[ImageResponse])
def get_images(house_id: int, db: Session = Depends(get_db)):
    """获取房源所有图片"""
    return queries.get_images(db, house_id)
