"""新建评估 API 路由"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.db.database import get_db
from backend.db import queries
from backend.models.assessment import AssessmentRequest, ReviewAddRequest, ScrapeRequest
from backend.services import assessment_service, review_analysis_service

router = APIRouter(prefix="/api/v1/assessments", tags=["assessments"])


@router.post("", status_code=201)
def create_assessment(payload: AssessmentRequest, db: Session = Depends(get_db)):
    """接收前端 /assess/new 表单提交的 payload，创建 House 和 Review 记录"""
    try:
        return assessment_service.create_assessment(db, payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{house_id}/analyze-reviews")
def analyze_reviews(house_id: int, db: Session = Depends(get_db)):
    """对指定房源的评论做六类风险关键词分析（规则引擎，不接 AI，不落库）"""
    house = queries.get_house(db, house_id)
    if not house:
        raise HTTPException(status_code=404, detail="房源不存在")
    return review_analysis_service.analyze_reviews(db, house_id)


@router.post("/{house_id}/reviews", status_code=201)
def add_review(house_id: int, payload: ReviewAddRequest, db: Session = Depends(get_db)):
    """给已有房源补充一条评价"""
    house = queries.get_house(db, house_id)
    if not house:
        raise HTTPException(status_code=404, detail="房源不存在")
    try:
        return assessment_service.add_review(db, house_id, payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/scrape")
def scrape_url(payload: ScrapeRequest):
    """抓取房源链接，提取房屋基本信息（小区名、租金、户型、面积等）"""
    result = assessment_service.scrape_listing(payload)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result
