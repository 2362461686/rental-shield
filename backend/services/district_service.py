"""区域统计服务层"""
from sqlalchemy.orm import Session
from backend.db.models import House
from backend.models.house import DistrictStats, DistrictComparison, DistrictRiskBreakdown
from backend import utils, config


def get_district_stats(db: Session, district: str = None) -> dict:
    """获取指定区域或所有区域的统计信息"""
    q = db.query(House)
    if district:
        q = q.filter(House.district == district)

    houses = q.all()
    if not houses:
        if district:
            return {
                "district": district,
                "house_count": 0, "avg_price": 0, "min_price": 0, "max_price": 0,
                "avg_sunlight": 0, "avg_noise": 0,
                "risk_breakdown": {"low": 0, "medium": 0, "high": 0}
            }
        return None

    prices = [h.price for h in houses if h.price]
    light_hours = []
    noise_dbs = []
    risk_levels = {"low": 0, "medium": 0, "high": 0}

    for h in houses:
        light = utils.simulate_sunlight(
            h.orientation, h.floor or 1, h.total_floors or 1, h.window_type or "普通窗")
        noise = utils.simulate_noise(
            h.building_type or "塔楼", h.building_year or 2010, h.floor or 1,
            h.total_floors or 1, h.distance_to_street or 999, h.has_business_below or False)

        light_hours.append(light["hours"])
        noise_dbs.append(noise["db"])

        # Risk calculation
        risk_score = 100
        if light["level"] == "差": risk_score -= 25
        elif light["level"] == "中": risk_score -= 10
        if noise["level"] == "差": risk_score -= 25
        elif noise["level"] == "中": risk_score -= 10
        market = config.MARKET_RENT.get(h.district, {}).get(h.layout, h.price)
        if market and market > 0:
            dev = (h.price - market) / market
            if dev > 0.2:
                risk_score -= 15

        if risk_score >= 80:
            risk_levels["low"] += 1
        elif risk_score >= 50:
            risk_levels["medium"] += 1
        else:
            risk_levels["high"] += 1

    return {
        "house_count": len(houses),
        "avg_price": round(sum(prices) / len(prices), 0) if prices else 0,
        "min_price": min(prices) if prices else 0,
        "max_price": max(prices) if prices else 0,
        "avg_sunlight": round(sum(light_hours) / len(light_hours), 1) if light_hours else 0,
        "avg_noise": round(sum(noise_dbs) / len(noise_dbs), 1) if noise_dbs else 0,
        "risk_breakdown": risk_levels,
    }


def get_all_district_stats(db: Session) -> DistrictComparison:
    """获取所有区域的对比统计"""
    from backend.db.models import House as HouseModel
    districts = db.query(HouseModel.district).distinct().all()
    district_list = [d[0] for d in districts]

    stats_list = []
    total_price = 0
    total_count = 0

    for d in district_list:
        stats = get_district_stats(db, d)
        if stats["house_count"] > 0:
            stats_list.append(DistrictStats(
                district=d,
                house_count=stats["house_count"],
                avg_price=stats["avg_price"],
                min_price=stats["min_price"],
                max_price=stats["max_price"],
                avg_sunlight=stats["avg_sunlight"],
                avg_noise=stats["avg_noise"],
                risk_breakdown=DistrictRiskBreakdown(**stats["risk_breakdown"]),
            ))
            total_price += stats["avg_price"] * stats["house_count"]
            total_count += stats["house_count"]

    avg_all = round(total_price / total_count, 0) if total_count > 0 else 0
    return DistrictComparison(
        districts=stats_list,
        total_houses=total_count,
        avg_price_all=avg_all,
    )
