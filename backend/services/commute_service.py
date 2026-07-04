"""高德地图通勤计算服务"""
import httpx
from backend.config import AMAP_API_KEY


async def calc_transit_time(
    origin_lat: float, origin_lng: float,
    dest_lat: float, dest_lng: float,
    city: str = "广州",
) -> int | None:
    """计算两地之间公共交通通勤时间（分钟）

    Args:
        origin_lat, origin_lng: 起点经纬度（房源位置）
        dest_lat, dest_lng: 终点经纬度（工作地点）
        city: 城市名

    Returns:
        通勤时间（分钟），API 不可用时返回 None
    """
    if not AMAP_API_KEY:
        return None

    url = "https://restapi.amap.com/v3/direction/transit/integrated"
    params = {
        "key": AMAP_API_KEY,
        "origin": f"{origin_lng},{origin_lat}",
        "destination": f"{dest_lng},{dest_lat}",
        "city": city,
        "strategy": "0",  # 最快捷模式
    }

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, params=params, timeout=15)
            data = resp.json()
            if data.get("status") == "1" and data.get("route", {}).get("transits"):
                duration_seconds = int(data["route"]["transits"][0].get("duration", 0))
                return duration_seconds // 60
    except Exception:
        pass

    return None


def commute_score_from_duration(minutes: int) -> float:
    """将通勤时间转换为 0-100 评分"""
    if minutes < 20:
        return 100.0
    elif minutes < 40:
        return 80.0
    elif minutes < 60:
        return 50.0
    else:
        return 20.0


def euclidean_distance_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """计算两点间直线距离（公里），用于 API 降级估算"""
    import math
    R = 6371.0  # 地球半径
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlng / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def estimate_commute_from_distance(distance_km: float) -> int:
    """根据直线距离估算通勤时间（API 降级方案）
    假设：5km 内约 20 分钟，之后每公里 +3 分钟
    """
    if distance_km <= 5:
        return max(10, int(distance_km * 4))
    else:
        return 20 + int((distance_km - 5) * 3)
