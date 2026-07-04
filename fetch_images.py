"""
rental-shield 房源图片抓取脚本
从链家/贝壳/58同城抓取真实房源图片

运行方式：
    python fetch_images.py                  # 抓取全部50套房源
    python fetch_images.py --house-ids 1,5  # 只抓取指定房源
"""
import os
import sys
import re
import json
import time
import random
import shutil
import urllib.parse
import argparse
from datetime import datetime

import requests
from bs4 import BeautifulSoup

import config
from db import get_session, House, ListingImage

# ============================================================
# 反爬 HTTP 会话管理器
# ============================================================
class AntiBotSession:
    """管理 HTTP 会话，实现 UA 轮换、延迟、代理等反爬措施"""

    # 5 个真实浏览器 User-Agent，每次请求随机切换
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    ]

    # 完整浏览器请求头
    BASE_HEADERS = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Cache-Control": "max-age=0",
    }

    def __init__(self):
        self.session = requests.Session()
        # 设置 Clash 代理
        self.session.proxies.update(config.SCRAPER_PROXY)
        self._rotate_ua()

    def _rotate_ua(self):
        """随机选择一个 User-Agent 并设置基础请求头"""
        self.session.headers.update(self.BASE_HEADERS)
        self.session.headers["User-Agent"] = random.choice(self.USER_AGENTS)

    def get(self, url, delay_range=None, timeout=20):
        """
        发送 GET 请求，带随机延迟、UA 轮换和错误处理

        参数：
            url: 请求 URL
            delay_range: (min, max) 延迟秒数范围，默认使用 config 配置
            timeout: 超时秒数

        返回：
            requests.Response 对象，失败返回 None
        """
        if delay_range is None:
            delay_range = (config.REQUEST_DELAY_MIN, config.REQUEST_DELAY_MAX)

        delay = random.uniform(*delay_range)
        time.sleep(delay)
        self._rotate_ua()

        try:
            resp = self.session.get(url, timeout=timeout, allow_redirects=True)
            resp.raise_for_status()
            return resp
        except requests.RequestException as e:
            print(f"  [HTTP错误] {url[:80]}...: {e}")
            return None

    def download_image(self, url, save_path):
        """下载单张图片到本地"""
        try:
            resp = self.get(url, delay_range=(0.3, 1.0), timeout=15)
            if resp is None:
                return False
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            with open(save_path, "wb") as f:
                f.write(resp.content)
            return True
        except Exception as e:
            print(f"  [下载失败] {url[:60]}...: {e}")
            return False


# ============================================================
# 平台搜索器：按小区名搜索房源
# ============================================================
class PlatformSearcher:
    """在各租房平台搜索小区名，获取真实房源链接"""

    def __init__(self, session):
        self.session = session

    def search(self, community, max_results=3):
        """
        按优先级依次尝试各个平台，搜索小区名

        参数：
            community: 小区名称
            max_results: 每个平台最多取多少条结果

        返回：
            list of dict: [{"platform": "链家", "url": "https://...", "title": "..."}]
        """
        for platform_cfg in config.SEARCH_PLATFORMS:
            name = platform_cfg["name"]
            search_url_fmt = platform_cfg["search_url"]
            base_url = platform_cfg["base_url"]

            try:
                encoded = urllib.parse.quote(community)
                search_url = search_url_fmt.format(encoded)
                print(f"  -> [{name}] 搜索: {search_url[:80]}...")

                resp = self.session.get(search_url, delay_range=(1.5, 3.0))
                if resp is None:
                    continue

                soup = BeautifulSoup(resp.text, "html.parser")
                results = self._extract_links(soup, base_url, name, max_results)

                if results:
                    print(f"  [{name}] 找到 {len(results)} 条结果")
                    return results
                else:
                    print(f"  [{name}] 无结果，尝试下一平台...")
            except Exception as e:
                print(f"  [{name}] 搜索异常: {e}")
                continue

        return []

    def _extract_links(self, soup, base_url, platform_name, max_results):
        """从搜索结果页 HTML 中提取房源链接"""
        results = []

        # 链家/贝壳的通用选择器
        selectors = [
            ".content__list--item a.content__list--item--aside",  # 链家/贝壳
            ".houseList a",  # 通用
            ".list-con a.img",  # 58同城
            "#house-lst li a",  # 58同城
            "a[href*='/zufang/']",  # 宽泛匹配
        ]

        for sel in selectors:
            for link in soup.select(sel):
                href = link.get("href", "")
                if not href or "javascript" in href:
                    continue
                # 补全 URL
                if href.startswith("//"):
                    href = "https:" + href
                elif href.startswith("/"):
                    href = base_url + href
                elif not href.startswith("http"):
                    continue
                # 过滤非租房页面
                if any(kw in href for kw in ["/zufang/", "/chuzu/"]):
                    title = link.get("title", "") or link.get_text(strip=True)
                    results.append({
                        "platform": platform_name,
                        "url": href,
                        "title": title[:50],
                    })
                if len(results) >= max_results:
                    break
            if results:
                break

        return results


# ============================================================
# 图片提取器：从房源详情页提取图片 URL
# ============================================================
class ImageExtractor:
    """从房源详情页提取图片 URL"""

    # 链家系 CDN 图片 URL 正则
    CDN_PATTERNS = [
        r'(https?://[^"\'<>\s]+?\.lianjia\.com[^"\'<>\s]*?\.(?:jpg|jpeg|png|webp))',
        r'(https?://[^"\'<>\s]+?\.ke\.com[^"\'<>\s]*?\.(?:jpg|jpeg|png|webp))',
        r'(https?://[^"\'<>\s]+?image[^"\'<>\s]*?\.(?:jpg|jpeg|png|webp))',
        r'data-src=["\']([^"\']+?(?:jpg|jpeg|png|webp)[^"\']*?)["\']',
    ]

    def __init__(self, session):
        self.session = session

    def extract(self, listing_url, max_images=10):
        """
        访问房源详情页，提取图片 URL

        三策略：img 标签 → JSON-LD 结构化数据 → 正则扫描
        """
        print(f"  访问房源页: {listing_url[:80]}...")
        resp = self.session.get(listing_url, delay_range=(1.0, 2.0))
        if resp is None:
            return []

        soup = BeautifulSoup(resp.text, "html.parser")
        image_urls = []

        # 策略1：提取页面中的 <img> 标签
        for img in soup.select("img[src], img[data-src], img[data-original]"):
            src = img.get("src") or img.get("data-src") or img.get("data-original")
            if src and any(ext in src.lower() for ext in [".jpg", ".jpeg", ".png", ".webp"]):
                image_urls.append(self._normalize_url(src))

        # 策略2：解析 JSON-LD 结构化数据
        for script in soup.select('script[type="application/ld+json"]'):
            try:
                data = json.loads(script.string)
                for photo in data.get("photo", []):
                    if isinstance(photo, dict) and "contentUrl" in photo:
                        image_urls.append(self._normalize_url(photo["contentUrl"]))
            except (json.JSONDecodeError, TypeError):
                continue

        # 策略3：正则扫描完整 HTML
        html = resp.text
        for pattern in self.CDN_PATTERNS:
            urls = re.findall(pattern, html, re.IGNORECASE)
            for url in urls:
                image_urls.append(self._normalize_url(url))

        # 去重并限制数量
        seen = set()
        unique_urls = []
        for url in image_urls:
            if url not in seen:
                seen.add(url)
                unique_urls.append(url)
            if len(unique_urls) >= max_images:
                break

        return unique_urls

    def _normalize_url(self, url):
        """标准化 URL：补全协议头、去除参数"""
        if url.startswith("//"):
            return "https:" + url
        return url


# ============================================================
# 占位图生成（兜底方案）
# ============================================================
def generate_placeholder_svg(house_dir, filename, text):
    """
    生成 SVG 占位图，保证每个房源至少有一张图片

    参数：
        house_dir: 图片保存目录
        filename: 文件名
        text: 图片上显示的文字
    """
    svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" width="800" height="600" viewBox="0 0 800 600">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#e8eaf6;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#c5cae9;stop-opacity:1" />
    </linearGradient>
  </defs>
  <rect width="800" height="600" fill="url(#bg)"/>
  <rect x="200" y="200" width="400" height="200" rx="15" fill="white" opacity="0.8"/>
  <text x="400" y="280" text-anchor="middle" fill="#5c6bc0" font-size="22" font-family="Microsoft YaHei, sans-serif">
    {text}
  </text>
  <text x="400" y="320" text-anchor="middle" fill="#9fa8da" font-size="14" font-family="Microsoft YaHei, sans-serif">
    图片暂缺 · 请以实地看房为准
  </text>
  <text x="400" y="500" text-anchor="middle" fill="#bdbdbd" font-size="11" font-family="sans-serif">
    Rental-Shield · 广州站
  </text>
</svg>'''

    filepath = os.path.join(house_dir, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(svg_content)
    return filepath


# ============================================================
# 主抓取流程
# ============================================================
def fetch_all_images(house_ids=None, max_per_house=None, min_per_house=None):
    """
    主函数：遍历房源 → 搜索 → 提取图片 → 下载 → 存入数据库

    参数：
        house_ids: 指定房源ID列表，None 表示全部
        max_per_house: 每个房源最多抓取图片数
        min_per_house: 每个房源最少图片数（不足时用占位图补齐）
    """
    if max_per_house is None:
        max_per_house = config.MAX_IMAGES_PER_HOUSE
    if min_per_house is None:
        min_per_house = config.MIN_IMAGES_PER_HOUSE

    session = get_session()

    # 查询房源
    if house_ids:
        houses = session.query(House).filter(House.id.in_(house_ids)).all()
    else:
        houses = session.query(House).all()

    total = len(houses)
    print(f"开始抓取 {total} 套房源图片（每套 {min_per_house}-{max_per_house} 张）")
    print(f"代理: {config.SCRAPER_PROXY['http']}")
    print("=" * 60)

    # 清空旧图片
    session.query(ListingImage).delete()
    session.commit()

    # 清空图片文件夹
    images_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), config.IMAGES_DIR)
    if os.path.exists(images_dir):
        shutil.rmtree(images_dir)
    os.makedirs(images_dir, exist_ok=True)

    # 初始化爬虫组件
    bot = AntiBotSession()
    searcher = PlatformSearcher(bot)
    extractor = ImageExtractor(bot)

    stats = {"success": 0, "partial": 0, "failed": 0, "total_images": 0}

    for idx, house in enumerate(houses):
        community = house.community
        print(f"\n[{idx+1}/{total}] {community} ({house.district})")

        # 步骤1：搜索小区
        search_results = searcher.search(community)

        # 步骤2：提取图片
        image_urls = []
        for result in search_results:
            urls = extractor.extract(result["url"], max_images=max_per_house)
            if urls:
                image_urls = urls
                break  # 取第一个有图片的房源

        # 去重
        image_urls = list(dict.fromkeys(image_urls))[:max_per_house]

        # 步骤3：下载图片
        house_dir = os.path.join(images_dir, str(house.id))
        os.makedirs(house_dir, exist_ok=True)

        downloaded = 0
        for i, img_url in enumerate(image_urls):
            ext = os.path.splitext(urllib.parse.urlparse(img_url).path)[1]
            if not ext or ext not in [".jpg", ".jpeg", ".png", ".webp"]:
                ext = ".jpg"
            filename = f"{i+1:03d}{ext}"
            filepath = os.path.join(house_dir, filename)
            rel_path = os.path.join(config.IMAGES_DIR, str(house.id), filename)

            if bot.download_image(img_url, filepath):
                downloaded += 1
                stats["total_images"] += 1

                session.add(ListingImage(
                    house_id=house.id,
                    image_path=rel_path,
                    source_url=img_url,
                    sort_order=i + 1,
                    is_primary=(i == 0),
                ))

        # 步骤4：不足时生成占位图
        need_placeholder = max(min_per_house - downloaded, 0)
        for pi in range(need_placeholder):
            idx_in_list = downloaded + pi + 1
            filename = f"{idx_in_list:03d}.svg"
            rel_path = os.path.join(config.IMAGES_DIR, str(house.id), filename)
            generate_placeholder_svg(house_dir, filename, house.community)

            session.add(ListingImage(
                house_id=house.id,
                image_path=rel_path,
                source_url="",
                sort_order=idx_in_list,
                is_primary=(downloaded == 0 and pi == 0),
            ))
            stats["total_images"] += 1

        session.commit()

        # 统计
        if downloaded >= min_per_house:
            stats["success"] += 1
            print(f"  ✅ 成功 {downloaded} 张")
        elif downloaded > 0:
            stats["partial"] += 1
            print(f"  ⚠️ 仅 {downloaded} 张，补充 {min_per_house - downloaded} 张占位图")
        else:
            stats["failed"] += 1
            print(f"  ❌ 未获取到图片，使用 {min_per_house} 张占位图")

    session.close()

    print("\n" + "=" * 60)
    print(f"抓取完成！成功={stats['success']} 部分={stats['partial']} 失败={stats['failed']} 总图片={stats['total_images']}")
    return stats


# ============================================================
# 命令行入口
# ============================================================
def main():
    import sys as _sys
    if hasattr(_sys.stdout, 'reconfigure'):
        _sys.stdout.reconfigure(encoding='utf-8')
    parser = argparse.ArgumentParser(description="rental-shield 房源图片抓取脚本")
    parser.add_argument("--house-ids", type=str, default=None,
                        help="指定房源ID，逗号分隔（默认抓取全部），如 1,3,5,10")
    parser.add_argument("--max-per-house", type=int, default=None,
                        help=f"每套房源最多图片数（默认{config.MAX_IMAGES_PER_HOUSE}）")
    parser.add_argument("--min-per-house", type=int, default=None,
                        help=f"每套房源最少图片数（默认{config.MIN_IMAGES_PER_HOUSE}）")
    args = parser.parse_args()

    house_ids = None
    if args.house_ids:
        house_ids = [int(x.strip()) for x in args.house_ids.split(",")]

    fetch_all_images(
        house_ids=house_ids,
        max_per_house=args.max_per_house,
        min_per_house=args.min_per_house,
    )


if __name__ == "__main__":
    main()
