"""分析相关 API 路由（物理模拟 + 市场价比较）"""
from fastapi import APIRouter, Body
from backend import utils
from backend import config
from backend.models.analysis import SunlightResult, NoiseResult, PriceAnalysis

router = APIRouter(prefix="/api/v1/analysis", tags=["analysis"])


@router.post("/sunlight", response_model=SunlightResult)
def calculate_sunlight(
    orientation: str = Body(...),
    floor: int = Body(...),
    total_floors: int = Body(...),
    window_type: str = Body(...),
):
    """光照模拟计算"""
    return utils.simulate_sunlight(orientation, floor, total_floors, window_type)


@router.post("/noise", response_model=NoiseResult)
def calculate_noise(
    building_type: str = Body(...),
    building_year: int = Body(...),
    floor: int = Body(...),
    total_floors: int = Body(...),
    distance_to_street: int = Body(...),
    has_business_below: bool = Body(...),
):
    """噪声模拟计算"""
    return utils.simulate_noise(building_type, building_year, floor, total_floors,
                                 distance_to_street, has_business_below)


@router.post("/price", response_model=PriceAnalysis)
def analyze_price(
    district: str = Body(...),
    layout: str = Body(...),
    price: int = Body(...),
):
    """价格与市场价比较"""
    market = config.MARKET_RENT.get(district, {}).get(layout, price)
    dev = (price - market) / market if market else 0
    return PriceAnalysis(market_price=market, deviation=round(dev, 4), is_reasonable=abs(dev) <= 0.2)
