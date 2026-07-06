"""链家爬虫 — 通过页面解析获取广州租房数据"""
import requests, re
from bs4 import BeautifulSoup
from backend.crawlers.base import BaseCrawler

class LianjiaCrawler(BaseCrawler):
    source = "lianjia"
    base_url = "https://gz.lianjia.com"

    def fetch_listings(self, city: str = "广州", page: int = 1) -> list[dict]:
        results = []
        url = f"https://gz.lianjia.com/zufang/pg{page}/"
        try:
            resp = requests.get(url, headers=self.headers, timeout=15)
            if resp.status_code != 200:
                return results
            resp.encoding = "utf-8"
        except Exception:
            return results

        soup = BeautifulSoup(resp.text, "html.parser")
        items = soup.select(".content__list--item")
        for item in items:
            try:
                title_el = item.select_one(".content__list--item--title a")
                title = title_el.get_text(strip=True) if title_el else ""
                link = title_el.get("href", "") if title_el else ""

                price_el = item.select_one(".content__list--item-price em")
                price = int(re.sub(r"\D", "", price_el.get_text())) if price_el else 0

                desc_parts = item.select(".content__list--item--des")
                community_text = ""
                layout_text = ""
                area_val = 0
                district_text = ""
                if desc_parts:
                    text = desc_parts[0].get_text(" ", strip=True)
                    parts = [p.strip() for p in text.split("/")]
                    if len(parts) >= 1:
                        community_text = parts[0]
                    if len(parts) >= 2:
                        layout_text = parts[1]
                    if len(parts) >= 3:
                        am = re.search(r"(\d+)", parts[2])
                        area_val = float(am.group(1)) if am else 0
                loc_el = item.select_one(".content__list--item--des a")
                if loc_el:
                    district_text = loc_el.get_text(strip=True)

                if price > 0 and (community_text or title):
                    results.append({
                        "title": title or f"{community_text}{layout_text}",
                        "community": community_text,
                        "price": price,
                        "layout": layout_text,
                        "area": area_val,
                        "district": district_text,
                        "source_url": f"{self.base_url}{link}" if link.startswith("/") else link,
                        "source": self.source,
                    })
            except Exception:
                continue
        return results
