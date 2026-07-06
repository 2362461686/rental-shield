"""爬虫管理 API 路由"""
from fastapi import APIRouter, Query
from backend.crawlers.manager import CrawlerManager

router = APIRouter(prefix="/api/v1/crawler", tags=["crawler"])


@router.get("/sources")
def list_sources():
    """列出所有可用的爬虫数据源"""
    return {"sources": CrawlerManager.list_sources()}


@router.get("/status")
def get_status():
    """获取爬虫运行状态"""
    return CrawlerManager.get_status()


@router.post("/run/{source}")
def run_crawler(
    source: str,
    city: str = Query("广州", description="城市"),
    pages: int = Query(3, ge=1, le=10, description="爬取页数"),
):
    """手动触发爬虫"""
    return CrawlerManager.run(source=source, city=city, max_pages=pages)
