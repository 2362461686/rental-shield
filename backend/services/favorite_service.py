"""收藏服务层"""
from sqlalchemy.orm import Session
from backend.db.models import Favorite
from backend import utils
from backend import config


def list_favorites_with_houses(db: Session):
    """获取所有收藏的房源摘要信息"""
    from backend.db.models import House

    favorites = db.query(Favorite).order_by(Favorite.created_at.desc()).all()
    results = []
    for fav in favorites:
        h = fav.house
        if not h:
            continue

        light = utils.simulate_sunlight(
            h.orientation or "", h.floor or 1, h.total_floors or 1, h.window_type or "普通窗"
        )
        noise = utils.simulate_noise(
            h.building_type or "塔楼", h.building_year or 2010, h.floor or 1,
            h.total_floors or 1, h.distance_to_street or 999,
            h.has_business_below or False,
        )

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
            "id": fav.id,
            "house_id": h.id,
            "house": {
                "id": h.id, "title": h.title, "district": h.district,
                "community": h.community or "", "layout": h.layout or "",
                "area": h.area or 0, "price": h.price or 0,
                "orientation": h.orientation or "",
                "floor": h.floor or 1, "total_floors": h.total_floors or 1,
                "sunlight_hours": light["hours"], "sunlight_level": light["level"],
                "noise_db": noise["db"], "noise_level": noise["level"],
                "risk_score": risk_score, "risk_label": utils.risk_label(risk_score),
                "primary_image_url": primary_img,
                "latitude": h.latitude, "longitude": h.longitude,
                "commute_duration": h.commute_duration, "commute_score": h.commute_score,
            },
            "created_at": fav.created_at.isoformat() if fav.created_at else None,
            "notes": fav.notes,
        })
    return results
