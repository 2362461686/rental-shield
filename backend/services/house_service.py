"""房产服务层"""
from sqlalchemy.orm import Session
from backend.db import queries
from backend.models.house import HouseSummary, HouseDetail
from backend import config
from backend import utils


def list_houses(db: Session, districts=None, layout=None, min_price=0, max_price=99999, sort_by="综合推荐", keyword=None):
    """查询房源列表，附加光照/噪声/风险计算并排序"""
    houses = queries.query_houses(db, districts, layout, min_price, max_price, keyword)

    results = []
    for h in houses:
        light = utils.simulate_sunlight(h.orientation, h.floor, h.total_floors, h.window_type)
        noise = utils.simulate_noise(h.building_type, h.building_year, h.floor, h.total_floors,
                                      h.distance_to_street, h.has_business_below)

        risk_score = 100
        if light["level"] == "差": risk_score -= 25
        elif light["level"] == "中": risk_score -= 10
        if noise["level"] == "差": risk_score -= 25
        elif noise["level"] == "中": risk_score -= 10
        market = config.MARKET_RENT.get(h.district, {}).get(h.layout, h.price)
        dev = (h.price - market) / market if market else 0
        if dev > 0.2:
            risk_score -= 15

        primary_img = None
        if h.images:
            primary_img = h.images[0].image_path

        results.append({
            "obj": h,
            "light": light,
            "noise": noise,
            "risk_score": risk_score,
            "risk_label": utils.risk_label(risk_score),
            "primary_img": primary_img,
        })

    # 排序
    if sort_by == "价格从低到高":
        results.sort(key=lambda x: x["obj"].price)
    elif sort_by == "价格从高到低":
        results.sort(key=lambda x: x["obj"].price, reverse=True)
    elif sort_by == "光照最优":
        results.sort(key=lambda x: x["light"]["hours"], reverse=True)
    elif sort_by == "隔音最优":
        results.sort(key=lambda x: x["noise"]["db"])

    # 转为 Pydantic 模型
    summaries = []
    for r in results:
        h = r["obj"]
        summaries.append(HouseSummary(
            id=h.id, title=h.title, district=h.district, community=h.community or "",
            layout=h.layout or "", area=h.area or 0, price=h.price or 0, orientation=h.orientation or "",
            floor=h.floor or 1, total_floors=h.total_floors or 1,
            sunlight_hours=r["light"]["hours"], sunlight_level=r["light"]["level"],
            noise_db=r["noise"]["db"], noise_level=r["noise"]["level"],
            risk_score=r["risk_score"], risk_label=r["risk_label"],
            primary_image_url=r["primary_img"],
            review_count=len(h.reviews) if h.reviews else 0,
            latitude=h.latitude, longitude=h.longitude,
            commute_duration=h.commute_duration, commute_score=h.commute_score,
        ))
    return summaries


def get_house_detail(db: Session, house_id: int):
    """获取房源详情，含所有预计算"""
    h = queries.get_house(db, house_id)
    if not h:
        return None

    light = utils.simulate_sunlight(h.orientation or "", h.floor or 1, h.total_floors or 1, h.window_type or "普通窗")
    noise = utils.simulate_noise(h.building_type or "塔楼", h.building_year or 2010, h.floor or 1,
                                  h.total_floors or 1, h.distance_to_street or 999,
                                  h.has_business_below or False)
    market = config.MARKET_RENT.get(h.district, {}).get(h.layout, h.price)
    dev = (h.price - market) / market if market else 0

    return HouseDetail(
        id=h.id, title=h.title, district=h.district, community=h.community or "",
        layout=h.layout or "", area=h.area or 0, price=h.price or 0,
        floor=h.floor or 1, total_floors=h.total_floors or 1,
        orientation=h.orientation or "", window_type=h.window_type or "普通窗",
        building_type=h.building_type or "", building_year=h.building_year or 0,
        distance_to_street=h.distance_to_street or 0, has_business_below=h.has_business_below or False,
        landlord_phone_hash=h.landlord_phone_hash, source_url=h.source_url,
        latitude=h.latitude, longitude=h.longitude,
        created_at=h.created_at,
        sunlight_hours=light["hours"], sunlight_level=light["level"],
        noise_db=noise["db"], noise_level=noise["level"],
        market_price=market, price_deviation=round(dev, 4), is_price_reasonable=abs(dev) <= 0.2,
    )
