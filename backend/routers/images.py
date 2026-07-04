"""图片 API 路由"""
import os
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from backend.models.image import ScrapeRequest, ScrapeStatus

router = APIRouter(prefix="/api/v1/images", tags=["images"])

# 项目根目录（backend/ 的上一级）
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@router.get("/{image_path:path}")
def serve_image(image_path: str):
    """提供图片文件（路径相对于 images/ 目录）"""
    full_path = os.path.join(PROJECT_ROOT, "images", image_path)
    if not os.path.exists(full_path):
        raise HTTPException(status_code=404, detail=f"图片不存在: {image_path}")
    return FileResponse(full_path)


@router.post("/scrape", response_model=ScrapeStatus)
def trigger_scrape(request: ScrapeRequest):
    """触发图片抓取（后台任务占位）"""
    return ScrapeStatus(
        job_id="pending",
        status="not_implemented",
        progress=0,
        total=len(request.house_ids) if request.house_ids else 50,
        errors=["Playwright scraper 将在 Phase 5 实现"],
    )
