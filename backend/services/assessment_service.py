"""新建评估的业务逻辑：创建 House + Review 记录"""
from typing import Optional
from sqlalchemy.orm import Session
import logging

from backend.db.models import House, Review
from backend.services import geocode_service
import re
import requests
from bs4 import BeautifulSoup

from backend.models.assessment import AssessmentRequest, ReviewAddRequest, ScrapeRequest

logger = logging.getLogger(__name__)


def _has_content(val: Optional[str]) -> bool:
    """判断字符串是否有有效内容（非空且非全空格）"""
    return bool(val and val.strip())


async def create_assessment(db: Session, payload: AssessmentRequest) -> dict:
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
        )
        # 尝试地理编码获取经纬度（best-effort，失败不影响流程）
        if payload.community or payload.district:
            try:
                address_parts = ["广州市"]
                if payload.district:
                    address_parts.append(payload.district)
                if payload.community:
                    address_parts.append(payload.community)
                full_address = "".join(address_parts)
                coords = await geocode_service.geocode(full_address, city="广州")
                if coords:
                    house.latitude = coords["latitude"]
                    house.longitude = coords["longitude"]
                    logger.info(f"Geocoded assessment house {house.id}: {full_address} -> ({coords['latitude']}, {coords['longitude']})")
                else:
                    logger.info(f"Geocoding returned no results for: {full_address}")
            except Exception as e:
                logger.warning(f"Geocoding skipped for house {house.id}: {e}")
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

    # Validate URL
    if not url.startswith(("http://", "https://")):
        return {"url": url, "error": "请输入完整的链接地址（以 http:// 或 https:// 开头）"}

    try:
        # Better anti-bot headers
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-US;q=0.7",
            "Accept-Encoding": "gzip, deflate, br",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
            "Sec-Ch-Ua": "\"Google Chrome\";v=\"131\", \"Chromium\";v=\"131\", \"Not_A Brand\";v=\"24\"",
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": "\"Windows\"",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
        }
        resp = requests.get(url, headers=headers, timeout=20, allow_redirects=True)
        resp.encoding = resp.apparent_encoding or "utf-8"
        soup = BeautifulSoup(resp.text, "html.parser")

        result = {"url": url}
        text = soup.get_text()
        text = re.sub(r'\s+', ' ', text)

        # ── 页面标题 ──
        title_tag = soup.find("title")
        if title_tag:
            title_text = title_tag.get_text(strip=True)
            result["title"] = title_text

        # ── 小区名 ── (multiple strategies)
        community = None

        # Strategy 1: meta tags
        for meta in soup.find_all("meta"):
            name = (meta.get("name", "") or meta.get("property", "") or "").lower()
            content = (meta.get("content", "") or "").strip()
            if content and ("小区" in name or "community" in name.lower()):
                community = content
                break

        # Strategy 2: common patterns in text
        if not community:
            patterns = [
                r'([\u4e00-\u9fa5a-zA-Z·]+(?:花园|家园|新村|新苑|花苑|华庭|雅苑|名都|名苑|绿洲|豪庭|华府|广场|城|湾|景|苑|庭|居|邸|舍|庄|园))',
            ]
            for pattern in patterns:
                m = re.search(pattern, text)
                if m:
                    community = m.group(1).strip()
                    break

        # Strategy 3: Look for structured data or breadcrumbs
        if not community:
            for selector in ['.community', '.resblock', '.xiaoqu', '[class*="community"]', '[class*="xiaoqu"]']:
                elem = soup.select_one(selector)
                if elem and elem.get_text(strip=True):
                    community = elem.get_text(strip=True)
                    break

        if community:
            result["community"] = community

        # ── 租金 ──
        for pattern in [r'(\d{3,5})\s*元/月', r'(\d{3,5})\s*元/每月', r'(\d{3,5})元', r'¥\s*(\d{3,5})']:
            m = re.search(pattern, text)
            if m:
                result["price"] = int(m.group(1))
                break

        # ── 户型 ──
        for pattern in [r'(\d室\d厅\d卫)', r'(\d室\d厅)', r'(\d室\d卫)']:
            m = re.search(pattern, text)
            if m:
                result["layout"] = m.group(1)
                break

        # ── 面积 ──
        for pattern in [r'(\d{2,3})\s*[㎡平米平方mM]', r'面积[：:]\s*(\d{2,3})']:
            m = re.search(pattern, text)
            if m:
                val = float(m.group(1))
                if 10 < val < 500:
                    result["area"] = val
                    break

        # ── 楼层 ──
        for pattern in [r'(?:共(\d+)层|(\d+)/(\d+)层|第(\d+)层|(\d+)楼)']:
            m = re.search(pattern, text)
            if m:
                nums = [g for g in m.groups() if g]
                if len(nums) >= 2:
                    result["floor"] = int(nums[0])
                    result["total_floors"] = int(nums[1])
                elif len(nums) == 1:
                    result["floor"] = int(nums[0])
                break

        # ── 朝向 ──
        for kw in ["南北通透", "南北", "南向", "东南", "西南", "东", "西", "北"]:
            if kw in text:
                result["orientation"] = kw.replace("向", "")
                break

        # ── 区域 ──
        for district in ["天河", "海珠", "番禺", "越秀", "荔湾", "白云", "黄埔", "花都", "增城", "南沙", "从化"]:
            if district in text:
                result["district"] = district
                break

        # If nothing useful was extracted
        if len(result) <= 1:  # only url
            return {"url": url, "error": "未能从页面提取到有效信息，请手动填写。提示：部分网站需要登录或使用JS渲染"}

        return result

    except requests.ConnectionError:
        return {"url": url, "error": "无法连接该网站，请检查网络或链接是否有效"}
    except requests.Timeout:
        return {"url": url, "error": "请求超时，网站响应太慢，请手动填写信息"}
    except requests.RequestException as e:
        return {"url": url, "error": f"请求失败: {str(e)[:60]}，请手动填写"}
    except Exception as e:
        return {"url": url, "error": f"页面解析失败，请手动填写信息（{str(e)[:40]}）"}
