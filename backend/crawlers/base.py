"""爬虫基类 — 统一接口、频率控制、错误重试"""
import time, random, logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

class BaseCrawler(ABC):
    source: str = "unknown"               # 数据来源标识
    base_url: str = ""                    # 平台基础 URL
    min_interval: float = 3.0             # 最小请求间隔（秒）
    max_retries: int = 2                  # 最大重试次数
    headers: dict = {}

    def __init__(self):
        self._last_request = 0
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate",
            "Cache-Control": "no-cache",
        }

    def _rate_limit(self):
        """频率控制"""
        elapsed = time.time() - self._last_request
        if elapsed < self.min_interval:
            time.sleep(self.min_interval - elapsed)
        self._last_request = time.time()

    @abstractmethod
    def fetch_listings(self, city: str = "广州", page: int = 1) -> list[dict]:
        """抓取房源列表，返回 [{title, community, price, layout, area, ...}, ...]"""
        pass

    def run(self, city: str = "广州", max_pages: int = 5) -> int:
        """执行抓取任务，返回抓取数量"""
        total = 0
        for page in range(1, max_pages + 1):
            for attempt in range(self.max_retries + 1):
                try:
                    self._rate_limit()
                    listings = self.fetch_listings(city=city, page=page)
                    if listings:
                        total += len(listings)
                        logger.info(f"[{self.source}] page {page}: {len(listings)} listings")
                    break
                except Exception as e:
                    if attempt == self.max_retries:
                        logger.error(f"[{self.source}] page {page} failed: {e}")
                    else:
                        wait = (attempt + 1) * 2
                        logger.warning(f"[{self.source}] page {page} retry {attempt+1} after {wait}s")
                        time.sleep(wait)
            if page < max_pages:
                time.sleep(random.uniform(1, 2))
        return total
