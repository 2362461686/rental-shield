"""豆瓣租房小组爬虫（带频率控制和重试）"""
import re, time, random, logging
from bs4 import BeautifulSoup
from curl_cffi import requests as cffi_requests
from backend.crawlers.base import BaseCrawler

logger = logging.getLogger(__name__)

GUANGZHOU_GROUPS = [
    ("https://www.douban.com/group/tianhezufang/discussion", "天河租房"),
    ("https://www.douban.com/group/haizhuzufang/discussion", "海珠租房"),
    ("https://www.douban.com/group/zhufang/discussion", "租房"),
]

UAS = [
    "api-client/1 com.douban.frodo/7.18.0 iOS/17.0",
    "api-client/1 com.douban.frodo/7.20.0 Android/14",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 Mobile/15E148",
]

class DoubanCrawler(BaseCrawler):
    source = "douban"
    min_interval = 8.0  # 每组请求间隔8秒

    def fetch_listings(self, city: str = "广州", page: int = 1) -> list[dict]:
        results = []
        start = (page - 1) * 25
        for group_url, group_name in GUANGZHOU_GROUPS:
            if city != "广州" and city not in group_name:
                continue
            time.sleep(random.uniform(3, 6))  # 组间延迟
            url = f"{group_url}?start={start}"
            headers = {
                "User-Agent": random.choice(UAS),
                "Accept": "text/html,application/xhtml+xml",
                "Accept-Language": "zh-CN,zh;q=0.9",
            }
            try:
                r = cffi_requests.get(url, headers=headers, impersonate="chrome131", timeout=15)
                if r.status_code != 200:
                    logger.warning(f"Douban {group_name}: HTTP {r.status_code}")
                    continue
            except Exception as e:
                logger.warning(f"Douban {group_name}: {e}")
                continue

            soup = BeautifulSoup(r.text, "html.parser")
            posts = soup.select("td.title a")
            for p in posts:
                text = (p.get_text(strip=True) or "")
                if not any(k in text for k in ["出租", "整租", "合租", "转租", "找室友", "单间", "一房", "两房", "loft"]):
                    continue
                price_match = re.search(r"(\d{3,5})", text)
                price = int(price_match.group(1)) if price_match else 0
                community = self._extract_community(text)
                district = self._infer_district(text)
                rent_type = "整租" if any(k in text for k in ["整租", "一房", "两房", "三房"]) else "合租"
                if price > 0:
                    results.append({
                        "title": text[:100], "price": price,
                        "community": community or text[:30], "district": district,
                        "rent_type": rent_type, "source": self.source,
                        "source_url": p.get("href", ""),
                    })
        return results

    def _extract_community(self, text: str) -> str:
        for p in [r"([\u4e00-\u9fa5·]+(?:花园|家园|新村|新苑|花苑|华庭|雅苑|公寓|小区|广场|城|湾|景|苑|庭))"]:
            m = re.search(p, text)
            if m: return m.group(1)
        return ""

    def _infer_district(self, text: str) -> str:
        kw = {
            "天河": ["天河", "体育西", "石牌", "员村", "车陂", "东圃", "珠江新城", "猎德", "潭村", "岗顶", "华师", "五山", "棠下", "林和西"],
            "海珠": ["海珠", "昌岗", "江南西", "客村", "赤岗", "琶洲", "大塘", "沥滘", "宝岗大道", "中大", "晓港"],
            "番禺": ["番禺", "大石", "市桥", "汉溪长隆", "南村万博", "厦滘", "洛溪", "钟村", "南浦"],
            "越秀": ["越秀", "公园前", "淘金", "东山口", "烈士陵园", "北京路", "农讲所", "杨箕", "小北", "区庄", "团一大"],
            "荔湾": ["荔湾", "芳村", "花地湾", "西朗", "长寿路", "陈家祠", "中山八", "如意坊"],
            "白云": ["白云", "嘉禾", "永泰", "同和", "京溪", "梅花园", "黄边", "白云大道北", "太和"],
            "黄埔": ["黄埔", "萝岗", "科学城", "香雪", "文冲", "大沙地", "鱼珠"],
        }
        for d, kws in kw.items():
            if any(k in text for k in kws): return d
        return ""
