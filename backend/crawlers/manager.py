"""爬虫管理器 — 调度、去重、落地到数据库"""
import time, json, logging
from datetime import datetime
from sqlalchemy.orm import Session

from backend.db.models import House
from backend.db.database import SessionLocal
from backend.services import geocode_service
from backend.crawlers.beike import BeikeCrawler
from backend.crawlers.lianjia import LianjiaCrawler
from backend.crawlers.douban import DoubanCrawler

logger = logging.getLogger(__name__)

CRAWLERS = {
    "beike": BeikeCrawler(),
    "lianjia": LianjiaCrawler(),
    "douban": DoubanCrawler(),
}

_crawl_status = {
    "running": False,
    "current_source": None,
    "total_crawled": 0,
    "last_run": None,
    "errors": [],
}


class CrawlerManager:
    @staticmethod
    def list_sources() -> list[str]:
        return list(CRAWLERS.keys())

    @staticmethod
    def get_status() -> dict:
        return _crawl_status

    @staticmethod
    def run(source: str, city: str = "广州", max_pages: int = 5) -> dict:
        if source not in CRAWLERS:
            return {"error": f"Unknown source: {source}"}
        crawler = CRAWLERS[source]
        _crawl_status["running"] = True
        _crawl_status["current_source"] = source
        _crawl_status["errors"] = []
        try:
            listings = crawler.fetch_listings(city=city, page=1)
            for page in range(2, max_pages + 1):
                time.sleep(1)
                page_listings = crawler.fetch_listings(city=city, page=page)
                if page_listings:
                    listings.extend(page_listings)
                else:
                    break
            saved = CrawlerManager._save_to_db(listings)
            _crawl_status["total_crawled"] = saved
            _crawl_status["last_run"] = datetime.now().isoformat()
            return {"source": source, "crawled": len(listings), "saved": saved, "status": "ok"}
        except Exception as e:
            _crawl_status["errors"].append(str(e))
            return {"source": source, "error": str(e)}
        finally:
            _crawl_status["running"] = False

    @staticmethod
    def _save_to_db(listings: list[dict]) -> int:
        """将爬取结果落地到数据库，去重"""
        db: Session = SessionLocal()
        saved = 0
        try:
            for item in listings:
                source_url = item.get("source_url", "")
                if source_url:
                    existing = db.query(House).filter(House.source_url == source_url).first()
                    if existing:
                        continue
                h = House(
                    title=item.get("title", ""),
                    community=item.get("community", ""),
                    district=item.get("district", ""),
                    layout=item.get("layout", ""),
                    area=item.get("area", 0),
                    price=item.get("price", 0),
                    source_url=source_url,
                    floor=item.get("floor"),
                    total_floors=item.get("total_floors"),
                    orientation=item.get("orientation", ""),
                    window_type="普通窗",
                    distance_to_street=50,
                    has_business_below=False,
                )
                db.add(h)
                saved += 1
            db.commit()
        except Exception as e:
            db.rollback()
            logger.error(f"Save failed: {e}")
        finally:
            db.close()
        return saved
