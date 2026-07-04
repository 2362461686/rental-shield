"""
rental-shield 后端配置
"""
import os

# DeepSeek API
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
DEEPSEEK_BASE_URL = "https://api.deepseek.com"
DEEPSEEK_MODEL = "deepseek-chat"

# 数据库（backend 层级访问）
DATABASE_URL = "sqlite:///../rental.db"

# 广州各区市场参考租金（元/月）
MARKET_RENT = {
    "天河": {"一室": 3500, "两室": 5500},
    "海珠": {"一室": 2800, "两室": 4300},
    "番禺": {"一室": 1800, "两室": 2800},
    "越秀": {"一室": 3200, "两室": 5000},
    "荔湾": {"一室": 2500, "两室": 4000},
    "白云": {"一室": 1500, "两室": 2500},
}

GUANGZHOU_LATITUDE = 23.13
BASE_SUNLIGHT_HOURS = 4.5

ORIENTATION_WEIGHTS = {"南": 1.0, "东南": 0.85, "西南": 0.85, "东": 0.6, "西": 0.6, "东北": 0.4, "西北": 0.4, "北": 0.3}
WINDOW_COEFFICIENTS = {"落地窗": 1.2, "普通窗": 1.0, "小窗": 0.8}
BUILDING_NOISE = {"塔楼": 35, "板楼": 40, "自建房": 45}

# 高德地图 API Key
import os as _os
AMAP_API_KEY = _os.environ.get("AMAP_API_KEY", "")

# 广州各区中心坐标
DISTRICT_COORDS = {
    "天河": {"center_lat": 23.1250, "center_lng": 113.3612, "pinyin": "tianhe"},
    "海珠": {"center_lat": 23.0830, "center_lng": 113.3172, "pinyin": "haizhu"},
    "番禺": {"center_lat": 22.9380, "center_lng": 113.3545, "pinyin": "panyu"},
    "越秀": {"center_lat": 23.1291, "center_lng": 113.2670, "pinyin": "yuexiu"},
    "荔湾": {"center_lat": 23.1150, "center_lng": 113.2430, "pinyin": "liwan"},
    "白云": {"center_lat": 23.1580, "center_lng": 113.2750, "pinyin": "baiyun"},
}

# 爬虫代理
SCRAPER_PROXY = {"http": "http://127.0.0.1:7897", "https": "http://127.0.0.1:7897"}
IMAGES_DIR = "../images"
MIN_IMAGES_PER_HOUSE = 5
MAX_IMAGES_PER_HOUSE = 10
REQUEST_DELAY_MIN = 2.0
REQUEST_DELAY_MAX = 5.0

SEARCH_PLATFORMS = [
    {"name": "链家", "search_url": "https://gz.lianjia.com/zufang/rs{}/", "base_url": "https://gz.lianjia.com"},
    {"name": "贝壳", "search_url": "https://gz.ke.com/zufang/rs{}/", "base_url": "https://gz.ke.com"},
    {"name": "58同城", "search_url": "https://gz.58.com/zufang/?key={}", "base_url": "https://gz.58.com"},
]
