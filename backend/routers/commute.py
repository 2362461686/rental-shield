"""通勤计算 API 路由"""
from fastapi import APIRouter, Depends, Query, HTTPException, Body
from sqlalchemy.orm import Session
from typing import Optional

from backend.db.database import get_db
from backend.db.queries import get_house
from backend.db.models import WorkspaceConfig
from backend.services.commute_service import (
    calc_transit_time,
    commute_score_from_duration,
    euclidean_distance_km,
    estimate_commute_from_distance,
)


router = APIRouter(prefix="/api/v1/commute", tags=["commute"])


@router.get("/calculate")
async def calculate_commute(
    house_id: int = Query(..., description="房源ID"),
    workplace_lat: float = Query(..., description="工作地点纬度"),
    workplace_lng: float = Query(..., description="工作地点经度"),
    db: Session = Depends(get_db),
):
    """计算指定房源到工作地点的公交通勤时间"""
    house = get_house(db, house_id)
    if not house:
        raise HTTPException(status_code=404, detail="房源不存在")
    if house.latitude is None or house.longitude is None:
        raise HTTPException(status_code=400, detail="房源无坐标数据")

    # 尝试调用高德 API
    minutes = await calc_transit_time(
        house.latitude, house.longitude, workplace_lat, workplace_lng
    )

    # API 不可用时用直线距离估算
    is_estimated = False
    if minutes is None:
        dist_km = euclidean_distance_km(
            house.latitude, house.longitude, workplace_lat, workplace_lng
        )
        minutes = estimate_commute_from_distance(dist_km)
        is_estimated = True

    score = commute_score_from_duration(minutes)

    return {
        "house_id": house_id,
        "commute_duration": minutes,
        "commute_score": score,
        "is_estimated": is_estimated,
    }


@router.post("/workspace")
def save_workspace(
    name: str = Body(..., embed=True),
    lat: float = Body(..., embed=True),
    lng: float = Body(..., embed=True),
    db: Session = Depends(get_db),
):
    """保存工作地点配置"""
    # 取消所有旧活跃状态
    db.query(WorkspaceConfig).update({"is_active": False})
    config = WorkspaceConfig(
        workplace_name=name,
        workplace_lat=lat,
        workplace_lng=lng,
        is_active=True,
    )
    db.add(config)
    db.commit()
    db.refresh(config)
    return {
        "id": config.id,
        "workplace_name": config.workplace_name,
        "workplace_lat": config.workplace_lat,
        "workplace_lng": config.workplace_lng,
    }


@router.get("/workspace")
def get_workspace(db: Session = Depends(get_db)):
    """获取当前激活的工作地点配置"""
    config = db.query(WorkspaceConfig).filter(WorkspaceConfig.is_active == True).first()
    if not config:
        return {"configured": False}
    return {
        "configured": True,
        "id": config.id,
        "workplace_name": config.workplace_name,
        "workplace_lat": config.workplace_lat,
        "workplace_lng": config.workplace_lng,
    }


@router.delete("/workspace")
def clear_workspace(db: Session = Depends(get_db)):
    """清除工作地点配置"""
    db.query(WorkspaceConfig).update({"is_active": False})
    db.commit()
    return {"status": "cleared"}
