"""AI Agent 模块 — 从根目录 agents.py 适配 backend 环境"""
import json
import time
import config
from openai import OpenAI

# 跨层级导入：backend.agents -> 根目录 db.py
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db import get_house_reviews, get_houses_by_landlord, get_landlord_by_phone


def _get_client():
    return OpenAI(api_key=config.DEEPSEEK_API_KEY, base_url=config.DEEPSEEK_BASE_URL)


def _call_deepseek(system_prompt, user_prompt, max_retries=3):
    if not config.DEEPSEEK_API_KEY:
        return None
    client = _get_client()
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model=config.DEEPSEEK_MODEL,
                messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
                temperature=0.3, max_tokens=2000,
            )
            return response.choices[0].message.content
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
    return None


def _safe_json_parse(text, fallback):
    if not text: return fallback
    try:
        text = text.strip()
        if text.startswith("```"):
            lines = text.split("\n")
            text = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])
        return json.loads(text)
    except json.JSONDecodeError:
        return fallback


class ReviewMinerAgent:
    SYSTEM_PROMPT = """你是一个专业的租房体验分析师。请分析以下租客评论，提取'隔音''采光''房东''水电''交通''安全'六个维度的正面和负面关键词。输出JSON格式：{"sound":{"positive":[],"negative":[]}, ...}。只输出JSON。"""
    FEW_SHOT_EXAMPLE = """示例输入："房子朝南采光超好，白天完全不用开灯。但是晚上楼下大排档特别吵，一直闹到12点。房东人还不错，维修响应挺快的。"\n示例输出：{"sound":{"positive":[],"negative":["楼下大排档吵","闹到12点"]},"lighting":{"positive":["朝南采光好","不用开灯"],"negative":[]},"landlord":{"positive":["人不错","维修响应快"],"negative":[]},"utility":{"positive":[],"negative":[]},"transport":{"positive":[],"negative":[]},"safety":{"positive":[],"negative":[]}}"""

    def mine(self, house_id):
        reviews = get_house_reviews(house_id)
        empty = {d: {"positive": [], "negative": []} for d in ["sound","lighting","landlord","utility","transport","safety"]}
        if not reviews: return empty
        review_texts = "\n---\n".join([f"[{r.platform}] 评分{r.rating}/5: {r.content}" for r in reviews])
        user_prompt = f"{self.FEW_SHOT_EXAMPLE}\n\n现在请分析以下真实评论：\n{review_texts}"
        result_text = _call_deepseek(self.SYSTEM_PROMPT, user_prompt)
        return _safe_json_parse(result_text, empty)


class LandlordRiskAgent:
    SYSTEM_PROMPT = """你是一个租房风险调查员。根据该房东所有房源的租客评论，判断是否存在以下风险：押金不退、随意涨租、二房东转租、维修推诿、态度恶劣。输出JSON：{"risk_level":"高/中/低", "risk_items":[{"type":"风险类型","description":"具体风险描述及原文证据"}], "summary":"综合描述"}"""
    _FALLBACK = {"risk_level": "低", "risk_items": [], "summary": "AI 分析未启用"}

    def assess(self, landlord_phone_hash):
        houses = get_houses_by_landlord(landlord_phone_hash)
        if not houses: return {"risk_level": "低", "risk_items": [], "summary": "该房东暂无房源记录"}
        all_reviews = []
        for h in houses:
            all_reviews.extend(get_house_reviews(h.id))
        review_texts = "\n---\n".join([f"[房源{r.house_id}][{r.platform}]: {r.content}" for r in all_reviews])
        if not review_texts: return {"risk_level": "低", "risk_items": [], "summary": "暂无评论"}
        landlord = get_landlord_by_phone(landlord_phone_hash)
        lt = landlord.type if landlord else "未知"
        cc = landlord.complaint_count if landlord else 0
        prompt = f"房东类型：{lt}\n历史投诉次数：{cc}次\n\n该房东名下所有房源的租客评论如下：\n{review_texts}\n\n请分析风险并输出JSON。"
        result = _call_deepseek(self.SYSTEM_PROMPT, prompt)
        if result: return _safe_json_parse(result, self._FALLBACK)
        return {"risk_level": "低", "risk_items": [], "summary": "AI 分析未启用"}


class FinalAdvisorAgent:
    SYSTEM_PROMPT = """你是一个毕业生租房顾问。综合以下信息：光照评级、隔音评级、价格是否合理、评论挖掘结果、房东风险等级，给出最终建议。输出JSON：{"decision":"推荐/可考虑/不推荐", "risk_level":"红/黄/绿", "summary":"综合建议文本", "highlights":["优点"], "warnings":["缺点"]}"""
    _FALLBACK = {"decision": "可考虑", "risk_level": "黄", "summary": "AI 分析未启用，建议实地看房后决定。", "highlights": ["自动评估"], "warnings": ["建议实地考察"]}

    def advise(self, light_score, noise_score, price_deviation, review_data, landlord_risk):
        prompt = f"""请综合分析以下广州房源信息：\n【物理环境】\n- 光照：{light_score['level']}（日均 {light_score['hours']} 小时）\n- 噪声：{noise_score['level']}（预计 {noise_score['db']} dB）\n【价格分析】\n- 市场参考价：{price_deviation.get('market_price','N/A')} 元/月\n- 价格偏离：{price_deviation.get('deviation',0):.1%}\n- 是否合理：{'是' if price_deviation.get('is_reasonable',True) else '否'}\n【评论挖掘】\n{json.dumps(review_data, ensure_ascii=False, indent=2)}\n【房东风险】\n- 等级：{landlord_risk.get('risk_level','未知')}\n- 风险点：{json.dumps(landlord_risk.get('risk_items',[]), ensure_ascii=False)}\n- 描述：{landlord_risk.get('summary','无')}\n\n请给出最终建议 JSON。"""
        result = _call_deepseek(self.SYSTEM_PROMPT, prompt)
        if result: return _safe_json_parse(result, self._FALLBACK)
        # 规则引擎降级
        score = 0
        hl, wn = [], []
        if light_score['level'] == "优": score += 25; hl.append(f"采光极佳（{light_score['hours']}h）")
        elif light_score['level'] == "良": score += 18; hl.append(f"采光良好（{light_score['hours']}h）")
        elif light_score['level'] == "差": wn.append(f"采光差（{light_score['hours']}h）")
        else: score += 10
        if noise_score['level'] == "优": score += 25; hl.append(f"环境安静（{noise_score['db']}dB）")
        elif noise_score['level'] == "良": score += 18; hl.append(f"噪声可控（{noise_score['db']}dB）")
        elif noise_score['level'] == "差": wn.append(f"噪声大（{noise_score['db']}dB）")
        else: score += 10
        if price_deviation.get('is_reasonable', True): score += 25
        else: score += 10; wn.append("价格偏高")
        rl = landlord_risk.get('risk_level','低')
        if rl == "低": score += 25
        elif rl == "高": wn.append("房东高风险")
        else: score += 12
        if score >= 80: d, r = "推荐", "绿"
        elif score >= 50: d, r = "可考虑", "黄"
        else: d, r = "不推荐", "红"
        return {"decision": d, "risk_level": r, "summary": f"综合评分 {score}/100。{'值得推荐。' if d=='推荐' else '可实地考察后决定。' if d=='可考虑' else '建议多看几家。'}", "highlights": hl[:5], "warnings": wn[:5]}
