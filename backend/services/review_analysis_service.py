"""评论关键词分析服务（纯规则引擎，不接 AI）"""
from sqlalchemy.orm import Session
from backend.db.models import Review

# ── 六类风险的关键词库 ──
CATEGORY_RULES = {
    "noise": {
        "label": "noise",
        "negative": ["吵", "噪音", "噪声", "广场舞", "装修", "施工", "马路", "临街",
                     "飞机", "火车", "KTV", "夜市", "大排档", "隔壁吵", "楼上吵",
                     "楼下吵", "脚步声", "隔音差", "不隔音", "很吵", "太吵", "嘈杂",
                     "狗叫", "宠物叫", "小孩哭", "打麻将"],
        "positive": ["安静", "隔音好", "隔音不错", "清静", "不吵", "很安静", "宁静",
                     "隔音效果不错"],
    },
    "sunlight": {
        "label": "sunlight",
        "negative": ["阴暗", "潮湿", "发霉", "暗", "没阳光", "见不到光", "不透风",
                     "闷", "西晒", "晒死", "暴晒", "霉味", "不通风", "采光差",
                     "晒不到", "没光", "黑", "阴冷", "返潮"],
        "positive": ["采光好", "阳光好", "明亮", "通风", "通透", "光线好", "朝南",
                     "采光不错", "阳光充足", "视野好"],
    },
    "landlord": {
        "label": "landlord",
        "negative": ["黑心", "坑", "坑人", "态度差", "不维修", "不管", "不修",
                     "推诿", "踢皮球", "二房东", "中介费贵", "不给修", "联系不上",
                     "找不到人", "不理人", "耍赖", "随意涨价", "乱涨价", "加租",
                     "不配合", "扯皮", "赖账"],
        "positive": ["房东好", "靠谱", "负责", "态度好", "配合", "维修及时",
                     "人不错", "好沟通", "好说话", "热心"],
    },
    "deposit": {
        "label": "deposit",
        "negative": ["不退押金", "扣押金", "克扣", "押金不退", "扣钱", "乱扣",
                     "扣我押金", "押金被扣", "违约金高", "押金纠纷", "不退钱",
                     "找借口扣", "无理扣"],
        "positive": ["押金全退", "押金退了", "退还押金", "退押金", "押金退了"],
    },
    "commute": {
        "label": "commute",
        "negative": ["交通不便", "没地铁", "地铁远", "公交少", "走路太远", "太远",
                     "不方便", "通勤久", "班车少", "没公交", "挤地铁", "堵车",
                     "远", "偏僻"],
        "positive": ["交通方便", "近地铁", "地铁近", "BRT", "公交方便", "走路就到",
                     "通勤方便", "地铁口", "公交站近", "地铁站近"],
    },
    "safety": {
        "label": "safety",
        "negative": ["不安全", "小偷", "偷窃", "盗窃", "被偷", "门禁坏", "没保安",
                     "消防隐患", "电线老化", "火灾", "可疑", "恐怖", "抢劫",
                     "尾随", "没门禁", "闲杂人", "乱"],
        "positive": ["安全", "保安", "门禁", "监控", "刷卡", "刷脸", "物业管理好",
                     "治安好", "放心", "安保"],
    },
}


def _score_category(rules: dict, reviews_text: list[str]) -> dict:
    """扫描评论文本，计算单类风险和证据

    返回值：
      level   — low / medium / high / unknown
      score   — 0 ~ 100
      evidence — 命中的原文上下文片段
    """
    neg_set = set(rules["negative"])
    pos_set = set(rules["positive"])

    matched_neg = set()
    matched_pos = set()
    evidence = []

    for text in reviews_text:
        for kw in neg_set:
            if kw in text:
                matched_neg.add(kw)
                # 截取关键词上下文作为证据
                idx = text.find(kw)
                start = max(0, idx - 8)
                end = min(len(text), idx + len(kw) + 12)
                snippet = text[start:end].strip()
                if start > 0:
                    snippet = "…" + snippet
                if end < len(text):
                    snippet = snippet + "…"
                if snippet not in evidence:
                    evidence.append(snippet)
        for kw in pos_set:
            if kw in text:
                matched_pos.add(kw)

    # 计分：负面 +15，正面 -10，0-100
    raw = len(matched_neg) * 15 - len(matched_pos) * 10
    score = max(0, min(100, raw))

    if not matched_neg and not matched_pos:
        return {"level": "unknown", "score": 0, "evidence": []}

    if score == 0:
        level = "low"
    elif score <= 30:
        level = "medium"
    else:
        level = "high"

    return {"level": level, "score": score, "evidence": evidence[:5]}


def _recommendation(overall_level: str) -> str:
    """总风险等级 → 建议"""
    mapping = {"low": "recommend", "medium": "consider", "high": "reject"}
    return mapping.get(overall_level, "unknown")


def analyze_reviews(db: Session, house_id: int) -> dict:
    """评论关键词风险分析（纯规则引擎）

    返回：
      house_id
      source              — rules / none
      overall_risk_level  — low / medium / high / unknown
      overall_risk_score  — 0 ~ 100
      recommendation      — recommend / consider / reject / unknown
      total_reviews
      categories          — { noise: { level, score, evidence }, ... }
    """
    reviews = db.query(Review).filter(Review.house_id == house_id).all()

    # 无评论 / 空文本
    texts = [r.content for r in reviews if r.content and r.content.strip()]
    if not texts:
        return {
            "house_id": house_id,
            "source": "none",
            "overall_risk_level": "unknown",
            "overall_risk_score": 0,
            "recommendation": "unknown",
            "total_reviews": len(reviews),
            "categories": {},
        }

    # 对六类逐一评分
    categories = {}
    all_scores = []
    for cat_key, rules in CATEGORY_RULES.items():
        result = _score_category(rules, texts)
        result["label"] = rules["label"]
        categories[cat_key] = result
        if result["level"] != "unknown":
            all_scores.append(result["score"])

    # 综合风险
    overall_score = max(all_scores) if all_scores else 0
    if overall_score == 0:
        overall_level = "low"
    elif overall_score <= 30:
        overall_level = "medium"
    else:
        overall_level = "high"

    return {
        "house_id": house_id,
        "source": "rules",
        "overall_risk_level": overall_level,
        "overall_risk_score": overall_score,
        "recommendation": _recommendation(overall_level),
        "total_reviews": len(reviews),
        "categories": categories,
    }
