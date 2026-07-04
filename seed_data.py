"""
rental-shield 种子数据脚本
插入 50 条广州真实感房源数据，包含房源、评论、价格历史和房东信息
运行方式：python seed_data.py
"""
import random
import hashlib
from datetime import datetime, timedelta
from db import init_db, get_session, House, Review, PriceHistory, Landlord
import config

random.seed(42)  # 固定随机种子，确保每次生成的数据一致


def hash_phone(phone):
    """对手机号做哈希处理，保护隐私"""
    return hashlib.sha256(phone.encode()).hexdigest()[:16]


def generate_data():
    """生成并插入所有模拟数据"""
    session = get_session()

    # 清空旧数据（如果存在）
    for table in [PriceHistory, Review, House, Landlord]:
        session.query(table).delete()
    session.commit()

    # ============================================================
    # 一、创建 10 个房东（至少 3 个有投诉记录）
    # ============================================================
    landlord_data = [
        {"phone": "13800001001", "name": "张先生", "type": "一手房东", "complaint_count": 0, "risk_tags": ""},
        {"phone": "13800001002", "name": "李女士", "type": "一手房东", "complaint_count": 5, "risk_tags": "押金纠纷,维修推诿"},
        {"phone": "13800001003", "name": "王先生", "type": "二房东", "complaint_count": 3, "risk_tags": "随意涨租,二房东转租"},
        {"phone": "13800001004", "name": "赵女士", "type": "公寓托管", "complaint_count": 0, "risk_tags": ""},
        {"phone": "13800001005", "name": "陈先生", "type": "一手房东", "complaint_count": 0, "risk_tags": ""},
        {"phone": "13800001006", "name": "刘女士", "type": "一手房东", "complaint_count": 1, "risk_tags": "态度恶劣"},
        {"phone": "13800001007", "name": "黄先生", "type": "中介", "complaint_count": 8, "risk_tags": "押金不退,随意涨租,二房东转租,维修推诿,态度恶劣"},
        {"phone": "13800001008", "name": "周女士", "type": "一手房东", "complaint_count": 0, "risk_tags": ""},
        {"phone": "13800001009", "name": "吴先生", "type": "一手房东", "complaint_count": 0, "risk_tags": ""},
        {"phone": "13800001010", "name": "郑女士", "type": "一手房东", "complaint_count": 0, "risk_tags": ""},
    ]
    landlords = []
    for ld in landlord_data:
        l = Landlord(
            phone_hash=hash_phone(ld["phone"]),
            name=ld["name"],
            type=ld["type"],
            complaint_count=ld["complaint_count"],
            risk_tags=ld["risk_tags"],
        )
        session.add(l)
        landlords.append(l)
    session.commit()

    # ============================================================
    # 二、各区域房源配置
    # 区域分布：天河10, 海珠10, 番禺10, 越秀8, 荔湾7, 白云5
    # ============================================================
    district_config = [
        # (区域, 数量, 小区列表, 户型分布("一室"数量,"两室"数量)...)
        ("天河", 10, ["骏景花园", "中海康城", "华景新城", "天朗明居", "棠德花苑", "侨林苑", "东方新世界", "骏逸苑", "旭景家园", "美林湖畔"]),
        ("海珠", 10, ["光大花园", "江南新苑", "保利花园", "逸景翠园", "金碧花园", "翠城花园", "罗马家园", "愉景雅苑", "海富花园", "富力千禧"]),
        ("番禺", 10, ["祈福新邨", "华南新城", "广州雅居乐", "锦绣香江", "南国奥园", "星河湾", "丽江花园", "万科欧泊", "金山谷", "亚运城"]),
        ("越秀", 8, ["锦城花园", "富力广场", "东湖新村", "华侨新村", "小北花苑", "六榕小区", "农林上苑", "淘金家园"]),
        ("荔湾", 7, ["恒荔湾畔", "花地湾花园", "芳村花园", "四季花园", "荔港南湾", "富力唐宁", "新世界花园"]),
        ("白云", 5, ["岭南新世界", "白云高尔夫", "金碧雅苑", "万科金域蓝湾", "保利紫薇花园"]),
    ]

    # 户型分布规则
    layouts = ["一室"] * 20 + ["两室"] * 25 + ["三室及以上"] * 5
    random.shuffle(layouts)

    # 朝向分布
    orientations = ["南"] * 12 + ["北"] * 6 + ["东南"] * 8 + ["西南"] * 6 + ["东"] * 5 + ["西"] * 4 + ["东北"] * 5 + ["西北"] * 4
    random.shuffle(orientations)

    # 窗户类型分布
    window_types = ["落地窗"] * 10 + ["普通窗"] * 30 + ["小窗"] * 10
    random.shuffle(window_types)

    # 建筑类型分布
    building_types = ["塔楼"] * 25 + ["板楼"] * 20 + ["自建房"] * 5
    random.shuffle(building_types)

    house_id = 0
    houses_records = []

    for district, count, communities in district_config:
        for i in range(count):
            house_id += 1
            community = communities[i % len(communities)]

            # 随机分配户型
            layout = layouts.pop()

            # 根据户型和区域获取市场参考价，随机浮动 ±20%
            market_price = config.MARKET_RENT.get(district, {}).get(layout, 3000)
            price = int(market_price * random.uniform(0.8, 1.2))
            price = max(800, min(8000, price))  # 限制在合理范围内

            # 面积：一室 25-50m²，两室 55-90m²，三室 85-120m²
            if layout == "一室":
                area = random.randint(25, 50)
            elif layout == "两室":
                area = random.randint(55, 90)
            else:
                area = random.randint(85, 120)

            # 楼层和总楼层
            total_floors = random.choice([7, 9, 12, 18, 25, 32, 33])
            floor = random.randint(1, total_floors)

            # 各项属性随机分配
            orientation = orientations.pop()
            window_type = window_types.pop()
            building_type = building_types.pop()
            building_year = random.choice([1995, 1998, 2000, 2003, 2005, 2008, 2010, 2012, 2015, 2018, 2020, 2022])

            # 临街距离：至少 10 个房源临主街（<50m）
            if house_id <= 10:
                distance_to_street = random.randint(5, 45)
            else:
                distance_to_street = random.choice([random.randint(5, 45), random.randint(50, 200), random.randint(200, 500)])

            # 底商：15 个房源有底商
            has_business_below = house_id <= 15

            # 分配房东（循环使用 10 个房东）
            landlord_idx = (house_id - 1) % 10
            landlord_phone_hash = hash_phone(landlord_data[landlord_idx]["phone"])

            # 房源标题
            title = f"{community}{layout}丨{orientation}向丨{'精装修' if random.random() > 0.3 else '简装'}丨近地铁"

            house = House(
                id=house_id,
                title=title,
                district=district,
                community=community,
                layout=layout,
                area=area,
                price=price,
                floor=floor,
                total_floors=total_floors,
                orientation=orientation,
                window_type=window_type,
                building_type=building_type,
                building_year=building_year,
                distance_to_street=distance_to_street,
                has_business_below=has_business_below,
                landlord_phone_hash=landlord_phone_hash,
                source_url=f"https://gz.lianjia.com/zufang/GZ{100000 + house_id}.html",
                created_at=datetime.now() - timedelta(days=random.randint(1, 30)),
            )
            session.add(house)
            houses_records.append(house)
    session.commit()

    # ============================================================
    # 三、为每条房源插入 2-4 条评论
    # ============================================================
    # 预定义的评论模板（真实感评论，有具体槽点和优点）
    positive_templates = {
        "sound": ["隔音还不错，邻居也都比较安静", "小区整体安静，晚上睡得很踏实", "关上窗基本听不到外面声音"],
        "lighting": ["朝南采光超好，白天完全不用开灯", "阳光充足，晒衣服很方便", "早上阳光洒进来特别舒服", "采光还行，不算阴暗"],
        "landlord": ["房东人很好，维修响应挺快的", "房东比较实在，没那么多事", "签约很爽快，房东全程配合", "房东阿姨人很热心"],
        "utility": ["民用水电，费用正常", "水电是自己交的，没有中间加价", "电费比较便宜"],
        "transport": ["离地铁站走路5分钟，通勤方便", "楼下就是公交站，出行很方便", "三号线直达天河，上班不堵"],
        "safety": ["小区有24小时保安，感觉很安全", "门禁系统完善，外人进不来", "周边治安挺好"],
    }

    negative_templates = {
        "sound": ["晚上楼下大排档吵到12点，根本没法早睡", "隔音太差了，隔壁说话都能听清楚", "临街真的很吵，每天被车流声吵醒"],
        "lighting": ["采光不太好，白天也得开灯", "北向的，冬天特别暗", "窗户小，房间显得很暗"],
        "landlord": ["房东退押金拖了一个月，各种找理由扣钱", "签合同后房东态度完全变了", "房东半年涨了两次房租", "维修的事情推了好几次才处理"],
        "utility": ["水电费有点贵，感觉被加价了", "商业用电，夏天开空调电费爆炸"],
        "transport": ["离地铁站有点远，走路要15分钟以上", "附近在修路，出行不太方便"],
        "safety": ["晚上回家路上有点黑，不太安全", "城中村的房子，安全方面有点担心"],
    }

    platforms = ["小红书", "豆瓣", "链家"]

    for house in houses_records:
        # 每个房源 2-4 条评论
        num_reviews = random.randint(2, 4)
        for r in range(num_reviews):
            # 随机组合正面和负面评论
            selected_pos = []
            selected_neg = []

            # 根据朝向决定采光评论
            if house.orientation in ["南", "东南", "西南"]:
                selected_pos.append(random.choice(positive_templates["lighting"]))
            elif house.orientation in ["北", "西北", "东北"]:
                selected_neg.append(random.choice(negative_templates["lighting"]))

            # 根据临街和底商决定噪声评论
            if house.distance_to_street < 50 or house.has_business_below:
                if random.random() > 0.4:
                    selected_neg.append(random.choice(negative_templates["sound"]))
            else:
                if random.random() > 0.3:
                    selected_pos.append(random.choice(positive_templates["sound"]))

            # 根据房东投诉数决定房东评论
            landlord_data_item = landlord_data[house.id % 10]
            if landlord_data_item["complaint_count"] >= 3:
                if random.random() > 0.5:
                    selected_neg.append(random.choice(negative_templates["landlord"]))
            else:
                if random.random() > 0.5:
                    selected_pos.append(random.choice(positive_templates["landlord"]))

            # 随机添加 1-2 条其他维度的评论
            all_dimensions = ["sound", "lighting", "landlord", "utility", "transport", "safety"]
            random.shuffle(all_dimensions)
            for dim in all_dimensions[:2]:
                if random.random() > 0.6:
                    selected_pos.append(random.choice(positive_templates[dim]))
                elif random.random() > 0.3:
                    selected_neg.append(random.choice(negative_templates[dim]))

            # 组合评论内容
            content_parts = selected_pos[:2] + selected_neg[:1]
            random.shuffle(content_parts)
            content = "。".join(content_parts) + "。"

            # 根据正面/负面评论比例给出评分
            if len(selected_neg) == 0:
                rating = random.randint(4, 5)
            elif len(selected_pos) == 0:
                rating = random.randint(1, 2)
            else:
                rating = random.randint(2, 4)

            review = Review(
                house_id=house.id,
                platform=random.choice(platforms),
                content=content,
                rating=rating,
                created_at=datetime.now() - timedelta(days=random.randint(1, 180)),
            )
            session.add(review)
    session.commit()

    # ============================================================
    # 四、为每条房源插入 2-3 条价格历史记录
    # ============================================================
    for house in houses_records:
        base_price = house.price
        num_records = random.randint(2, 3)
        for i in range(num_records):
            # 每次价格在基础价上浮动 ±15%
            hist_price = int(base_price * random.uniform(0.85, 1.15))
            hist_price = max(800, min(8000, hist_price))
            record_date = datetime.now() - timedelta(days=random.randint(30, 365))
            session.add(PriceHistory(
                house_id=house.id,
                price=hist_price,
                record_date=record_date,
            ))
    session.commit()

    session.close()
    print(f"✅ 种子数据生成完成！共插入 {len(houses_records)} 套房源、{sum(2 + random.randint(0, 2) for _ in houses_records)} 条评论及对应价格历史。")


# ============================================================
# 主入口
# ============================================================
if __name__ == "__main__":
    print("🏠 rental-shield 数据初始化中...")
    init_db()  # 确保表已创建
    generate_data()
    print("🎉 全部数据已就绪！")
