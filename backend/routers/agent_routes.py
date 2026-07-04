"""AI Agent API 路由"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.db.database import get_db
from backend.db.queries import get_house, get_reviews
from backend.services.analysis_service import run_review_mining, run_landlord_risk, run_final_advice
from backend import utils, config

router = APIRouter(prefix="/api/v1/agents", tags=["agents"])


@router.post("/review-mining/{house_id}")
def review_mining(house_id: int):
    """AI 评论挖掘：分析指定房源的所有评论"""
    result = run_review_mining(house_id)
    return result


@router.post("/landlord-risk/{phone_hash}")
def landlord_risk(phone_hash: str):
    """AI 房东风险评估"""
    result = run_landlord_risk(phone_hash)
    return result


@router.post("/final-advice/{house_id}")
def final_advice(house_id: int, db: Session = Depends(get_db)):
    """AI 综合决策建议"""
    h = get_house(db, house_id)
    if not h:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="房源不存在")

    light = utils.simulate_sunlight(h.orientation or "", h.floor or 1, h.total_floors or 1, h.window_type or "普通窗")
    noise = utils.simulate_noise(h.building_type or "塔楼", h.building_year or 2010, h.floor or 1,
                                  h.total_floors or 1, h.distance_to_street or 999, h.has_business_below or False)
    market = config.MARKET_RENT.get(h.district, {}).get(h.layout, h.price)
    dev = (h.price - market) / market if market else 0
    price_info = {"market_price": market, "deviation": dev, "is_reasonable": abs(dev) <= 0.2}

    review_data = run_review_mining(house_id)
    landlord_risk_data = run_landlord_risk(h.landlord_phone_hash) if h.landlord_phone_hash else {"risk_level": "低", "risk_items": [], "summary": ""}

    result = run_final_advice(light, noise, price_info, review_data, landlord_risk_data)
    return result
