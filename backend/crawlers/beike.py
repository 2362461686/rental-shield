"""贝壳找房爬虫 — 通过公开 API 获取广州租房数据"""
import requests
from backend.crawlers.base import BaseCrawler

class BeikeCrawler(BaseCrawler):
    source = "beike"
    # 贝壳租房 API
    API_URL = "https://gz.ke.com/api/rent/resblock/list"
    base_url = "https://gz.ke.com"

    def __init__(self):
        super().__init__()
        self.headers.update({
            "Referer": "https://gz.ke.com/zufang/",
            "Origin": "https://gz.ke.com",
        })

    def fetch_listings(self, city: str = "广州", page: int = 1) -> list[dict]:
        results = []
        # 贝壳页面列表
        url = f"https://gz.ke.com/zufang/pg{page}/"
        try:
            resp = requests.get(url, headers=self.headers, timeout=15)
            if resp.status_code != 200:
                return results
        except Exception:
            return results

        from bs4 import BeautifulSoup
        import re
        soup = BeautifulSoup(resp.text, "html.parser")
        items = soup.select(".content__list--item")
        for item in items:
            try:
                title_el = item.select_one(".content__list--item--title a")
                title = title_el.get_text(strip=True) if title_el else ""
                link = title_el.get("href", "") if title_el else ""
                price_el = item.select_one(".content__list--item-price em")
                price = int(re.sub(r"\D", "", price_el.get_text())) if price_el else 0
                desc_els = item.select(".content__list--item--des a")
                desc_parts = [a.get_text(strip=True) for a in desc_els]
                community = desc_parts[0] if desc_parts else ""
                layout = desc_parts[1] if len(desc_parts) > 1 else ""
                area_text = desc_parts[2] if len(desc_parts) > 2 else ""
                area_match = re.search(r"(\d+)", area_text)
                area = float(area_match.group(1)) if area_match else 0
                loc_els = item.select(".content__list--item--des")[1].find_all("a") if len(item.select(".content__list--item--des")) > 1 else []
                district = loc_els[0].get_text(strip=True) if loc_els else ""

                if price > 0 and community:
                    results.append({
                        "title": title or f"{community}{layout}",
                        "community": community,
                        "price": price,
                        "layout": layout,
                        "area": area,
                        "district": district,
                        "source_url": f"https://gz.ke.com{link}" if link.startswith("/") else link,
                        "source": self.source,
                    })
            except Exception:
                continue
        return results
