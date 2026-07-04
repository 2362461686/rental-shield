"""区域统计 API 路由"""
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session

from backend.db.database import get_db
from backend.services import district_service
from backend.models.house import DistrictStats, DistrictComparison

router = APIRouter(prefix="/api/v1/districts", tags=["districts"])


@router.get("/stats", response_model=DistrictComparison)
def get_district_comparison(db: Session = Depends(get_db)):
    """获取所有区域的对比统计（房源数、均价、采光、隔音、风险分布）"""
    return district_service.get_all_district_stats(db)


@router.get("/stats/{district}", response_model=DistrictStats)
def get_single_district_stats(
    district: str,
    db: Session = Depends(get_db),
):
    """获取指定区域的详细统计"""
    stats = district_service.get_district_stats(db, district)
    if stats is None or stats["house_count"] == 0:
        raise HTTPException(status_code=404, detail=f"区域 '{district}' 不存在或无房源")
    return DistrictStats(
        district=district,
        **{k: v for k, v in stats.items() if k != "district"},
    )


@router.get("/list")
def list_districts(db: Session = Depends(get_db)):
    """获取所有区域名称及房源数量"""
    from backend.db.models import House as HouseModel
    from sqlalchemy import func
    result = (
        db.query(HouseModel.district, func.count(HouseModel.id))
        .group_by(HouseModel.district)
        .order_by(func.count(HouseModel.id).desc())
        .all()
    )
    return [{"district": r[0], "count": r[1]} for r in result]


@router.get("/geocode")
async def geocode_address(address: str = Query(..., description="地址文本，如：广州市天河区骏景花园")):
    """将地址文本转换为经纬度坐标（调用高德地理编码 API）"""
    from backend.services.geocode_service import geocode
    result = await geocode(address)
    if result is None:
        raise HTTPException(status_code=400, detail="地理编码失败，请检查地址是否正确或 API Key 是否已配置")
    return result
