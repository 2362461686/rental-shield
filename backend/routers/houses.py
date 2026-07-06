"""房源相关 API 路由"""
from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional

from backend.db.database import get_db
from backend.db import queries
from backend.db.models import House
from backend.services import house_service
from backend.models.house import HouseSummary, HouseDetail, ReviewResponse, PriceHistoryResponse, ImageResponse

router = APIRouter(prefix="/api/v1/houses", tags=["houses"])


# ── Fixed-path routes (MUST come before /{house_id}) ──

@router.get("/suggest")
def suggest_communities(
    q: str = Query(..., min_length=1),
    limit: int = Query(5, ge=1, le=20),
    db: Session = Depends(get_db),
):
    """搜索建议"""
    from difflib import get_close_matches
    rows = db.query(House.community).filter(House.community != None, House.community != "").distinct().all()
    all_names = [r[0] for r in rows if r[0]]
    exact = db.query(House.community).filter(House.community.like(f"%{q}%")).distinct().limit(limit).all()
    exact_names = [r[0] for r in exact]
    fuzzy = get_close_matches(q, all_names, n=limit, cutoff=0.3)
    suggestions = list(dict.fromkeys(exact_names + fuzzy))[:limit]
    return {"query": q, "suggestions": suggestions}


@router.get("/communities/stats")
def get_community_stats(db: Session = Depends(get_db)):
    """社区聚合统计"""
    rows = db.query(
        House.community, House.district, func.count(House.id).label("count"),
        func.avg(House.price).label("avg_price"),
    ).filter(House.community != None, House.community != "").group_by(House.community).all()
    return [{"community": r[0], "district": r[1], "count": r[2], "avg_price": round(r[3]) if r[3] else None} for r in rows]


@router.get("/landlords/{phone_hash}/houses")
def get_landlord_houses(phone_hash: str, db: Session = Depends(get_db)):
    """同一房东所有房源"""
    houses = queries.get_landlord_houses(db, phone_hash)
    return [{"id": h.id, "title": h.title, "district": h.district, "community": h.community, "price": h.price, "layout": h.layout, "risk_score": None} for h in houses]


# ── List (root) ──

@router.get("", response_model=list[HouseSummary])
def list_houses(
    response: Response,
    districts: Optional[str] = Query(None, description="区域，逗号分隔"),
    layout: Optional[str] = Query(None),
    min_price: int = Query(0),
    max_price: int = Query(8000),
    sort_by: str = Query("综合推荐"),
    keyword: Optional[str] = Query(None, description="关键词搜索（小区名、标题）"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(50, ge=1, le=100, description="每页条数"),
    db: Session = Depends(get_db),
):
    """房源列表查询，支持筛选、排序和分页"""
    district_list = [d.strip() for d in districts.split(",") if d.strip()] if districts else None
    all_results = house_service.list_houses(db, district_list, layout, min_price, max_price, sort_by, keyword)
    total = len(all_results)
    paginated = all_results[(page - 1) * page_size : page * page_size]
    response.headers["X-Total-Count"] = str(total)
    response.headers["X-Page"] = str(page)
    response.headers["X-Page-Size"] = str(page_size)
    return paginated


# ── Parameterized routes (/{house_id} and sub-resources) ──

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
