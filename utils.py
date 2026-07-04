"""
rental-shield 物理模拟算法模块
包含日照时长模拟、噪声等级模拟 和 风险标签判定

日照公式：
  最终日照小时 = 基准日照时长 × 朝向权重 × 楼层系数 × 窗户系数

噪声公式：
  最终噪声分贝 = 建筑基础噪声 + 年代修正 + 临街修正 + 底商修正 - 楼层衰减
"""
import config


# ============================================================
# 1. 日照时长模拟函数
# ============================================================
def simulate_sunlight_hours(orientation, floor, total_floors, window_type, district="天河"):
    """
    模拟房源日均有效日照时长

    计算公式：
        最终小时数 = 广州年均基准(4.5h) × 朝向权重 × 楼层系数 × 窗户系数

    参数：
        orientation (str): 朝向，如 "南"、"北"、"东南" 等
        floor (int): 所在楼层
        total_floors (int): 总楼层数
        window_type (str): 窗户类型，如 "落地窗"、"普通窗"、"小窗"
        district (str): 区域名称（预留参数，当前统一使用广州基准）

    返回：
        dict: {"hours": 日照小时数, "level": 评级(优/良/中/差)}
    """
    # --- Step 1: 获取朝向权重 ---
    # 南向采光最好，北向最差
    orientation_weight = config.ORIENTATION_WEIGHTS.get(orientation, 0.6)

    # --- Step 2: 计算楼层系数 ---
    # 低层（底部 1/3）：受周边建筑遮挡，乘以 0.7
    # 中层（中间 1/3）：部分遮挡，乘以 0.9
    # 高层（顶部 1/3）：视野开阔，乘以 1.1
    ratio = floor / max(total_floors, 1)
    if ratio <= 1 / 3:
        floor_coefficient = 0.7
    elif ratio <= 2 / 3:
        floor_coefficient = 0.9
    else:
        floor_coefficient = 1.1

    # --- Step 3: 获取窗户系数 ---
    # 落地窗采光面积大，小窗采光受限
    window_coefficient = config.WINDOW_COEFFICIENTS.get(window_type, 1.0)

    # --- Step 4: 计算最终日照小时数 ---
    hours = config.BASE_SUNLIGHT_HOURS * orientation_weight * floor_coefficient * window_coefficient
    hours = round(hours, 1)

    # --- Step 5: 评定日照等级 ---
    if hours > 5:
        level = "优"
    elif hours >= 3:
        level = "良"
    elif hours >= 1:
        level = "中"
    else:
        level = "差"

    return {"hours": hours, "level": level}


# ============================================================
# 2. 噪声等级模拟函数
# ============================================================
def simulate_noise_level(building_type, building_year, floor, total_floors,
                         distance_to_street, has_business_below, district="天河"):
    """
    模拟房源预计环境噪声分贝数

    计算公式：
        最终分贝 = 建筑基础噪声 + 建筑年代修正 + 临街距离修正 + 底商修正 - 楼层衰减

    参数：
        building_type (str): 建筑类型（塔楼/板楼/自建房）
        building_year (int): 建筑年代
        floor (int): 所在楼层
        total_floors (int): 总楼层数
        distance_to_street (int): 距主街道距离（米）
        has_business_below (bool): 是否有底商
        district (str): 区域名称（预留参数）

    返回：
        dict: {"db": 噪声分贝数, "level": 评级(优/良/中/差)}
    """
    # --- Step 1: 建筑类型基础噪声 ---
    # 塔楼隔音相对较好，自建房隔音差
    base_noise = config.BUILDING_NOISE.get(building_type, 40)

    # --- Step 2: 建筑年代修正 ---
    # 老房子隔音差，新房隔音标准更高
    if building_year < 2000:
        year_correction = 8
    elif building_year <= 2010:
        year_correction = 4
    else:
        year_correction = 0

    # --- Step 3: 临街距离修正 ---
    # 越靠近主街，交通噪声越大
    if distance_to_street < 50:
        street_correction = 20
    elif distance_to_street <= 200:
        street_correction = 10
    else:
        street_correction = 0

    # --- Step 4: 底商修正 ---
    # 底商带来人声、空调外机等额外噪声
    business_correction = 15 if has_business_below else 0

    # --- Step 5: 楼层衰减 ---
    # 越高层受地面噪声影响越小，每层减少约 0.5dB
    floor_attenuation = (total_floors - floor) * 0.5

    # --- Step 6: 计算最终噪声分贝 ---
    db = base_noise + year_correction + street_correction + business_correction - floor_attenuation
    db = round(max(db, 0), 1)  # 噪声不会低于 0dB

    # --- Step 7: 评定噪声等级 ---
    if db < 40:
        level = "优"
    elif db < 50:
        level = "良"
    elif db < 60:
        level = "中"
    else:
        level = "差"

    return {"db": db, "level": level}


# ============================================================
# 3. 风险标签判定函数
# ============================================================
def risk_label(score):
    """
    根据综合风险评分返回可视化标签

    参数：
        score (float): 综合评分（0-100）

    返回：
        str: 风险标签 emoji 字符串
    """
    if score >= 80:
        return "🟢 低风险"
    elif score >= 50:
        return "🟡 中等风险"
    else:
        return "🔴 高风险"
