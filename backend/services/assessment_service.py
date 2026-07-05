"""新建评估的业务逻辑：创建 House + Review 记录"""
from typing import Optional
from sqlalchemy.orm import Session

from backend.db.models import House, Review
import re
import requests
from bs4 import BeautifulSoup

from backend.models.assessment import AssessmentRequest, ReviewAddRequest, ScrapeRequest


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


def scrape_listing(payload: ScrapeRequest) -> dict:
    """抓取房源链接，提取房屋信息

    返回 dict: { url, community, district, price, layout, area, ... }
    抓取失败返回 { url, error }
    """
    url = payload.url.strip()
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        }
        resp = requests.get(url, headers=headers, timeout=15)
        resp.encoding = resp.apparent_encoding or "utf-8"
        soup = BeautifulSoup(resp.text, "html.parser")

        result = {"url": url}
        text = soup.get_text()

        # ── 小区名 ──
        community = None
        for meta in soup.find_all("meta"):
            name = meta.get("name", "") or meta.get("property", "")
            content = meta.get("content", "")
            if "小区" in name or "community" in name.lower():
                community = content.strip()
                break
        if not community:
            m = re.search(r"(?:小区|花园|家园|新村|新苑)[：:\s]*([\u4e00-\u9fa5a-zA-Z0-9·\-]+)", text)
            if m: community = m.group(0).strip()
        if community:
            result["community"] = community

        # ── 租金 ──
        m = re.search(r"(\d{3,5})\s*元/月", text)
        if m: result["price"] = int(m.group(1))

        # ── 户型 ──
        m = re.search(r"(\d室\d厅)", text)
        if m: result["layout"] = m.group(1)

        # ── 面积 ──
        m = re.search(r"(\d{2,3})\s*[㎡平米]", text)
        if m: result["area"] = float(m.group(1))

        # ── 楼层 ──
        m = re.search(r"(?:共(\d+)层|(\d+)/(\d+)层|(\d+)层)", text)
        if m:
            nums = [g for g in m.groups() if g]
            if len(nums) >= 2:
                result["floor"] = nums[0]
                result["total_floors"] = nums[1]
            elif len(nums) == 1:
                result["floor"] = nums[0]

        # ── 朝向 ──
        for kw in ["南", "南北", "东南", "西南", "东", "西", "北"]:
            if kw in text:
                result["orientation"] = kw
                break

        # ── 区域 ──
        for district in ["天河", "海珠", "番禺", "越秀", "荔湾", "白云"]:
            if district in text:
                result["district"] = district
                break

        # ── 页面标题 ──
        title_tag = soup.find("title")
        if title_tag:
            result["title"] = title_tag.get_text(strip=True)

        return result

    except requests.RequestException:
        return {"url": url, "error": "无法访问该链接，请检查 URL 是否正确"}
    except Exception:
        return {"url": url, "error": "页面解析失败，请手动填写信息"}
