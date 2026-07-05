"""评论关键词分析服务（DeepSeek 优先，规则引擎兜底）"""
import json
from typing import Optional
from sqlalchemy.orm import Session
from openai import OpenAI

from backend import config
from backend.db.models import Review

# ── 六类风险的关键词库（规则引擎兜底用） ──
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

CATEGORY_KEYS = ["noise", "sunlight", "landlord", "deposit", "commute", "safety"]

# ═══════════════════════════════════════════════════════
#  DeepSeek AI 分析（优先路径）
# ═══════════════════════════════════════════════════════

SYSTEM_PROMPT = """你是广州租房风险分析师。根据租客评论，分析六类风险并输出 JSON。

## 规则
- 只能基于评论原文分析，禁止编造任何信息
- 评论未提及的维度：level="unknown", score=0, evidence=[]
- evidence 必须是评论中的原文句子或短语，不可改写或编造
- 计分标准：0=低风险, 1-30=中风险, 31-100=高风险
- overall_risk_score 取六类中最高分

## 输出格式（只输出 JSON，禁止额外文字）
{
  "overall_risk_level": "low|medium|high",
  "overall_risk_score": 0,
  "categories": {
    "noise":    {"label":"noise",    "level":"low|medium|high|unknown", "score":0, "evidence":["原文片段"]},
    "sunlight": {"label":"sunlight", "level":"low|medium|high|unknown", "score":0, "evidence":["原文片段"]},
    "landlord": {"label":"landlord", "level":"low|medium|high|unknown", "score":0, "evidence":["原文片段"]},
    "deposit":  {"label":"deposit",  "level":"low|medium|high|unknown", "score":0, "evidence":["原文片段"]},
    "commute":  {"label":"commute",  "level":"low|medium|high|unknown", "score":0, "evidence":["原文片段"]},
    "safety":   {"label":"safety",   "level":"low|medium|high|unknown", "score":0, "evidence":["原文片段"]}
  }
}"""


def _call_deepseek(review_texts: list[str]) -> Optional[str]:
    """调用 DeepSeek，成功返回原始文本，失败返回 None"""
    if not config.DEEPSEEK_API_KEY:
        return None
    client = OpenAI(api_key=config.DEEPSEEK_API_KEY, base_url=config.DEEPSEEK_BASE_URL)
    user_prompt = "请分析以下租客评论（仅基于原文）：\n" + "\n---\n".join(review_texts)
    try:
        response = client.chat.completions.create(
            model=config.DEEPSEEK_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.05,
            max_tokens=3000,
        )
        return response.choices[0].message.content
    except Exception:
        return None


def _parse_deepseek_json(raw: Optional[str]) -> Optional[dict]:
    """解析 DeepSeek 返回的 JSON；剥离 ```json 包裹；失败返回 None"""
    if not raw:
        return None
    try:
        text = raw.strip()
        if text.startswith("```"):
            lines = text.split("\n")
            lo = 1 if lines[0].strip().startswith("```") else 0
            hi = -1 if lines and lines[-1].strip() == "```" else len(lines)
            text = "\n".join(lines[lo:hi])
        return json.loads(text)
    except (json.JSONDecodeError, TypeError):
        return None


def _is_valid_analysis(parsed: dict) -> bool:
    """基本校验：必须有 overall + categories 且六个分类齐全"""
    if not isinstance(parsed, dict):
        return False
    if "overall_risk_level" not in parsed:
        return False
    cats = parsed.get("categories", {})
    return all(k in cats for k in CATEGORY_KEYS)


def _try_deepseek_analysis(review_texts: list[str]) -> Optional[dict]:
    """尝试 DeepSeek 分析；任意环节失败返回 None → 回退规则版"""
    raw = _call_deepseek(review_texts)
    if raw is None:
        return None
    parsed = _parse_deepseek_json(raw)
    if parsed is None:
        return None
    if not _is_valid_analysis(parsed):
        return None
    return parsed


# ═══════════════════════════════════════════════════════
#  规则引擎（兜底路径）
# ═══════════════════════════════════════════════════════

def _score_category(rules: dict, reviews_text: list[str]) -> dict:
    """扫描评论文本，计算单类风险和证据"""
    neg_set = set(rules["negative"])
    pos_set = set(rules["positive"])

    matched_neg = set()
    matched_pos = set()
    evidence = []

    for text in reviews_text:
        for kw in neg_set:
            if kw in text:
                matched_neg.add(kw)
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
    mapping = {"low": "recommend", "medium": "consider", "high": "reject"}
    return mapping.get(overall_level, "unknown")


def _analyze_with_rules(texts: list[str]) -> dict:
    """规则引擎分析，返回 { overall_risk_level, overall_risk_score, categories }"""
    categories = {}
    all_scores = []
    for cat_key, rules in CATEGORY_RULES.items():
        result = _score_category(rules, texts)
        result["label"] = rules["label"]
        categories[cat_key] = result
        if result["level"] != "unknown":
            all_scores.append(result["score"])

    overall_score = max(all_scores) if all_scores else 0
    if overall_score == 0:
        overall_level = "low"
    elif overall_score <= 30:
        overall_level = "medium"
    else:
        overall_level = "high"

    return {
        "overall_risk_level": overall_level,
        "overall_risk_score": overall_score,
        "categories": categories,
    }


# ═══════════════════════════════════════════════════════
#  对外入口
# ═══════════════════════════════════════════════════════

def analyze_reviews(db: Session, house_id: int) -> dict:
    """评论风险分析：DeepSeek 优先 → 任意失败 → 规则引擎兜底

    返回结构（两种路径一致）：
      house_id, source, overall_risk_level, overall_risk_score,
      recommendation, total_reviews, categories
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

    # ── DeepSeek 优先 ──
    deepseek_result = _try_deepseek_analysis(texts)
    if deepseek_result is not None:
        overall_level = deepseek_result.get("overall_risk_level", "unknown")
        return {
            "house_id": house_id,
            "source": "deepseek",
            "overall_risk_level": overall_level,
            "overall_risk_score": deepseek_result.get("overall_risk_score", 0),
            "recommendation": _recommendation(overall_level),
            "total_reviews": len(reviews),
            "categories": deepseek_result.get("categories", {}),
        }

    # ── 规则引擎兜底 ──
    rules_result = _analyze_with_rules(texts)
    return {
        "house_id": house_id,
        "source": "rules",
        "overall_risk_level": rules_result["overall_risk_level"],
        "overall_risk_score": rules_result["overall_risk_score"],
        "recommendation": _recommendation(rules_result["overall_risk_level"]),
        "total_reviews": len(reviews),
        "categories": rules_result["categories"],
    }
