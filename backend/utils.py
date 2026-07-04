"""后端工具函数（光照/噪声模拟 + 风险标签）—— 从根目录 utils.py 复制保持独立"""
import config


def simulate_sunlight(orientation, floor, total_floors, window_type):
    weight = config.ORIENTATION_WEIGHTS.get(orientation, 0.6)
    ratio = floor / max(total_floors, 1)
    if ratio <= 1/3:
        fc = 0.7
    elif ratio <= 2/3:
        fc = 0.9
    else:
        fc = 1.1
    wc = config.WINDOW_COEFFICIENTS.get(window_type, 1.0)
    hours = round(config.BASE_SUNLIGHT_HOURS * weight * fc * wc, 1)
    if hours > 5: level = "优"
    elif hours >= 3: level = "良"
    elif hours >= 1: level = "中"
    else: level = "差"
    return {"hours": hours, "level": level}


def simulate_noise(building_type, building_year, floor, total_floors, distance_to_street, has_business_below):
    base = config.BUILDING_NOISE.get(building_type, 40)
    yc = 8 if building_year < 2000 else (4 if building_year <= 2010 else 0)
    sc = 20 if distance_to_street < 50 else (10 if distance_to_street <= 200 else 0)
    bc = 15 if has_business_below else 0
    fa = (total_floors - floor) * 0.5
    db = round(max(base + yc + sc + bc - fa, 0), 1)
    if db < 40: level = "优"
    elif db < 50: level = "良"
    elif db < 60: level = "中"
    else: level = "差"
    return {"db": db, "level": level}


def risk_label(score):
    if score >= 80: return "🟢 低风险"
    elif score >= 50: return "🟡 中等风险"
    return "🔴 高风险"
