"""
rental-shield FastAPI 应用入口
启动: uvicorn backend.main:app --reload --port 8000
访问: http://localhost:8000
"""
import os
import sys
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from backend.routers import houses, analysis, agent_routes, images, districts, commute, favorites, subway, assessments, crawler, chat

app = FastAPI(title="Rental-Shield API", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])


@app.on_event("startup")
async def startup():
    """启动时自动初始化数据库 + 启动后台爬虫"""
    from backend.db.database import init_db
    init_db()
    import asyncio
    from backend.crawlers.scheduler import background_crawl_loop
    asyncio.create_task(background_crawl_loop())

# API 路由
app.include_router(houses.router)
app.include_router(analysis.router)
app.include_router(agent_routes.router)
app.include_router(images.router)
app.include_router(districts.router)
app.include_router(commute.router)
app.include_router(favorites.router)
app.include_router(subway.router)
app.include_router(assessments.router)
app.include_router(crawler.router)
app.include_router(chat.router)


@app.get("/api/v1/health")
def health():
    return {"status": "ok", "version": "1.0.0"}


# 静态图片
images_dir = os.path.join(PROJECT_ROOT, "images")
os.makedirs(images_dir, exist_ok=True)

# 前端 dist 目录
frontend_dist = os.path.join(PROJECT_ROOT, "frontend", "dist")

if os.path.exists(frontend_dist):
    # 挂载前端资源（js/css等）
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_dist, "assets")), name="assets")

    # SPA catch-all: 所有非 API 请求返回 index.html
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        file_path = os.path.join(frontend_dist, full_path)
        if full_path and os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(frontend_dist, "index.html"))
