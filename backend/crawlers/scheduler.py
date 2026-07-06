"""爬虫调度器 — 启动时自动运行，定期刷新"""
import asyncio, logging, time
from datetime import datetime, timedelta
from backend.crawlers.manager import CrawlerManager

logger = logging.getLogger(__name__)

_last_run: dict = {}  # source -> timestamp


def run_all_sources_sync():
    """同步运行所有爬虫源，记录结果"""
    sources = CrawlerManager.list_sources()
    results = {}
    for source in sources:
        try:
            r = CrawlerManager.run(source=source, max_pages=2)
            results[source] = r
            _last_run[source] = time.time()
        except Exception as e:
            results[source] = {"error": str(e)}
            logger.error(f"Crawler {source} failed: {e}")
    return results


async def background_crawl_loop():
    """后台爬虫循环：首次 30s 后运行，之后每 30 分钟运行一次"""
    await asyncio.sleep(30)  # Wait for server to start
    logger.info("[Crawler] Background crawl loop started")
    while True:
        try:
            results = run_all_sources_sync()
            total = sum(r.get("saved", 0) for r in results.values() if isinstance(r, dict))
            if total > 0:
                logger.info(f"[Crawler] Saved {total} new listings from background crawl")
        except Exception as e:
            logger.error(f"[Crawler] Background error: {e}")
        await asyncio.sleep(1800)  # 30 minutes


def get_last_run_info():
    """获取各爬虫的上次运行时间"""
    return {s: datetime.fromtimestamp(t).isoformat() for s, t in _last_run.items()}
