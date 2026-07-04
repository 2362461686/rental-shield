"""地铁线路和站点 API 路由"""
from fastapi import APIRouter, Query, HTTPException
from typing import Optional
from backend.services import subway_service

router = APIRouter(prefix="/api/v1/subway", tags=["subway"])


@router.get("/lines")
def get_lines():
    """获取所有地铁线路列表"""
    return subway_service.get_all_lines()


@router.get("/lines/{line_name}")
def get_line_detail(line_name: str):
    """获取指定线路的所有站点"""
    result = subway_service.get_line_stations(line_name)
    if result is None:
        raise HTTPException(status_code=404, detail=f"线路 '{line_name}' 不存在")
    return result


@router.get("/stations")
def get_stations():
    """获取所有地铁站点（去重列表）"""
    return subway_service.get_all_stations()


@router.get("/nearby")
def get_nearby_stations(
    lat: float = Query(..., description="纬度"),
    lng: float = Query(..., description="经度"),
    max_distance: float = Query(1.5, description="最大距离（公里）"),
):
    """获取指定位置附近的地铁站"""
    return subway_service.find_nearby_stations(lat, lng, max_distance)


@router.get("/nearby-lines")
def get_nearby_lines(
    lat: float = Query(..., description="纬度"),
    lng: float = Query(..., description="经度"),
    max_distance: float = Query(1.5, description="最大距离（公里）"),
):
    """获取指定位置附近的地铁线路"""
    return subway_service.find_nearby_lines(lat, lng, max_distance)


@router.get("/commute")
def get_metro_commute(
    house_lat: float = Query(...),
    house_lng: float = Query(...),
    dest_lat: float = Query(...),
    dest_lng: float = Query(...),
):
    """基于地铁站点估算通勤时间"""
    result = subway_service.get_metro_commute_estimate(house_lat, house_lng, dest_lat, dest_lng)
    if result is None:
        raise HTTPException(status_code=400, detail="无法计算地铁通勤")
    return result
