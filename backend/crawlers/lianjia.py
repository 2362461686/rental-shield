"""链家爬虫 — Playwright 无头浏览器 + Cookie 管理"""
import re, time, random, logging
from bs4 import BeautifulSoup
from backend.crawlers.base import BaseCrawler

logger = logging.getLogger(__name__)

class LianjiaCrawler(BaseCrawler):
    source = "lianjia"
    base_url = "https://gz.lianjia.com"
    min_interval = 10.0

    def fetch_listings(self, city: str = "广州", page: int = 1) -> list[dict]:
        from playwright.sync_api import sync_playwright
        results = []
        city_map = {"广州": "gz", "北京": "bj", "深圳": "sz", "上海": "sh"}
        cc = city_map.get(city, "gz")
        url = f"https://{cc}.lianjia.com/zufang/"

        try:
            with sync_playwright() as p:
                b = p.chromium.launch(headless=True)
                ctx = b.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/131.0.0.0",
                    viewport={"width": 1366, "height": 768},
                    locale="zh-CN",
                )
                pg = ctx.new_page()
                # Visit homepage for cookies
                pg.goto(f"https://{cc}.lianjia.com/", timeout=30000, wait_until="domcontentloaded")
                time.sleep(1.5 + random.random())
                # Visit listings
                list_url = url if page == 1 else f"{url}pg{page}/"
                pg.goto(list_url, timeout=30000, wait_until="load")
                time.sleep(2.5 + random.random() * 2)
                soup = BeautifulSoup(pg.content(), "html.parser")

                for item in soup.select(".content__list--item"):
                    try:
                        title_el = item.select_one(".content__list--item--title a")
                        title = title_el.get_text(strip=True) if title_el else ""
                        href = title_el.get("href", "") if title_el else ""
                        price_el = item.select_one(".content__list--item-price em")
                        price = int(re.sub(r"\D", "", price_el.get_text())) if price_el else 0
                        # Parse description parts
                        desc_els = item.select(".content__list--item--des")
                        community = ""
                        if desc_els:
                            links = desc_els[0].find_all("a")
                            community = links[0].get_text(strip=True) if links else ""
                        district = ""
                        if len(item.select(".content__list--item--des")) > 1:
                            loc_links = item.select(".content__list--item--des")[1].find_all("a")
                            district = loc_links[0].get_text(strip=True) if loc_links else ""

                        if price > 0:
                            results.append({
                                "title": title or community,
                                "community": community,
                                "price": price,
                                "district": district,
                                "source_url": href,
                                "source": self.source,
                            })
                    except Exception:
                        continue
                b.close()
        except Exception as e:
            logger.error(f"Lianjia playwright: {e}")
        return results
