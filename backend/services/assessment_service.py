"""新建评估的业务逻辑：创建 House + Review 记录"""
from typing import Optional
from sqlalchemy.orm import Session

from backend.db.models import House, Review
from backend.models.assessment import AssessmentRequest, ReviewAddRequest


def _has_content(val: Optional[str]) -> bool:
    """判断字符串是否有有效内容（非空且非全空格）"""
    return bool(val and val.strip())


def create_assessment(db: Session, payload: AssessmentRequest) -> dict:
    """接收前端评估 payload，创建 House 记录并写入关联 Review

    返回 dict: { house_id, detail_url, message }
    """
    # 校验：title / source_url / community 至少有一个有效
    if not (_has_content(payload.title) or _has_content(payload.source_url) or _has_content(payload.community)):
        raise ValueError("请至少填写房源标题、房源链接或小区名中的一项")

    # 自动生成 title
    district = payload.district or "未知区域"
    title = payload.title
    if not title:
        parts = []
        if payload.district:
            parts.append(payload.district)
        if payload.community:
            parts.append(payload.community)
        if parts:
            title = "".join(parts) + "租房评估"
        else:
            title = "租房评估"

    # 过滤有效评价（content 非空且非全空格）
    valid_reviews = []
    if payload.reviews:
        for item in payload.reviews:
            content = (item.content or "").strip()
            if content:
                valid_reviews.append((item.platform or "user_input", content))

    try:
        # 创建 House 记录
        house = House(
            title=title,
            district=district,
            community=payload.community,
            layout=payload.layout,
            area=payload.area,
            price=payload.price,
            floor=payload.floor,
            total_floors=payload.total_floors,
            orientation=payload.orientation,
            window_type="普通窗",
            distance_to_street=payload.distance_to_street,
            has_business_below=payload.has_business_below or False,
            source_url=payload.source_url,
            # latitude / longitude 暂不填充（不做地理编码）
            # commute_destination 不写入 House 表
        )
        db.add(house)
        db.flush()  # 提前生成 house.id，以便 Review 关联

        # 写入 Review 记录
        review_count = 0
        for platform, content in valid_reviews:
            review = Review(
                house_id=house.id,
                platform=platform,
                content=content,
            )
            db.add(review)
            review_count += 1

        db.commit()
        db.refresh(house)  # 确保对象与数据库同步

    except Exception:
        db.rollback()
        raise

    return {
        "house_id": house.id,
        "detail_url": f"/house/{house.id}",
        "message": f"评估创建成功，已保存 {review_count} 条评价",
    }


def add_review(db: Session, house_id: int, payload: ReviewAddRequest) -> dict:
    """给已有房源补充一条评价

    返回 dict: { review_id, house_id, message }
    """
    content = (payload.content or "").strip()
    if not content:
        raise ValueError("评价内容不能为空")

    try:
        review = Review(
            house_id=house_id,
            platform=payload.platform or "user_input",
            content=content,
        )
        db.add(review)
        db.commit()
        db.refresh(review)
    except Exception:
        db.rollback()
        raise

    return {
        "review_id": review.id,
        "house_id": house_id,
        "message": "评价已添加",
    }
