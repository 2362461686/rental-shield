"""高德地图地理编码服务"""
import httpx
from backend.config import AMAP_API_KEY


async def geocode(address: str, city: str = "广州") -> dict | None:
    """将地址字符串转换为经纬度坐标

    Args:
        address: 完整地址文本，如 "广州市天河区骏景花园"
        city: 城市名，默认广州

    Returns:
        {"latitude": float, "longitude": float} 或 None
    """
    if not AMAP_API_KEY:
        return None

    url = "https://restapi.amap.com/v3/geocode/geo"
    params = {"key": AMAP_API_KEY, "address": address, "city": city}

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, params=params, timeout=10)
            data = resp.json()
            if data.get("status") == "1" and data.get("geocodes"):
                loc = data["geocodes"][0]["location"]
                lng_str, lat_str = loc.split(",")
                return {"latitude": float(lat_str), "longitude": float(lng_str)}
    except Exception:
        pass

    return None


async def reverse_geocode(lat: float, lng: float) -> dict | None:
    """将经纬度坐标转换为地址描述

    Args:
        lat: 纬度
        lng: 经度

    Returns:
        {"address": str, "district": str, "community": str} 或 None
    """
    if not AMAP_API_KEY:
        return None

    url = "https://restapi.amap.com/v3/geocode/regeo"
    params = {"key": AMAP_API_KEY, "location": f"{lng},{lat}"}

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, params=params, timeout=10)
            data = resp.json()
            if data.get("status") == "1" and data.get("regeocode"):
                regeo = data["regeocode"]
                addr_comp = regeo.get("addressComponent", {})
                return {
                    "address": regeo.get("formatted_address", ""),
                    "district": (
                        addr_comp.get("district", "") or ""
                    ),
                    "community": (
                        addr_comp.get("township", "") or ""
                    ),
                }
    except Exception:
        pass

    return None
