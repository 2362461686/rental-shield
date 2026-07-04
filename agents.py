"""
rental-shield AI Agent 模块
包含三个核心 Agent：评论挖掘、房东风险评估、最终决策顾问
所有 Agent 均通过 OpenAI 兼容模式调用 DeepSeek API

注意：如果 DEEPSEEK_API_KEY 未设置，Agent 将返回模拟数据以便离线测试
"""

import json
import time
import config
from db import get_house_reviews, get_houses_by_landlord, get_landlord_by_phone
from openai import OpenAI


# ============================================================
# DeepSeek API 客户端（OpenAI 兼容模式）
# ============================================================
def _get_client():
    """获取 DeepSeek API 客户端实例"""
    return OpenAI(api_key=config.DEEPSEEK_API_KEY, base_url=config.DEEPSEEK_BASE_URL)


def _call_deepseek(system_prompt, user_prompt, max_retries=3):
    """
    调用 DeepSeek API 的通用封装，支持重试

    参数：
        system_prompt (str): 系统提示词
        user_prompt (str): 用户输入
        max_retries (int): 最大重试次数

    返回：
        str: AI 返回的文本内容，失败返回 None
    """
    # 如果未配置 API Key，返回 None（调用方需自行处理降级逻辑）
    if not config.DEEPSEEK_API_KEY:
        return None

    client = _get_client()
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model=config.DEEPSEEK_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.3,  # 低温度确保输出稳定
                max_tokens=2000,
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"[DeepSeek API] 第 {attempt + 1} 次调用失败: {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # 指数退避重试
            else:
                print("[DeepSeek API] 已达最大重试次数，返回 None")
    return None


def _safe_json_parse(text, fallback):
    """
    安全解析 JSON 字符串

    参数：
        text (str): AI 返回的原始文本
        fallback (dict): 解析失败时的默认值

    返回：
        dict: 解析后的 JSON 字典
    """
    if not text:
        return fallback
    try:
        # 尝试提取 JSON 代码块（兼容 markdown 包裹的情况）
        text = text.strip()
        if text.startswith("```"):
            lines = text.split("\n")
            text = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])
        return json.loads(text)
    except json.JSONDecodeError:
        print(f"[JSON 解析失败] 原始返回: {text[:200]}...")
        return fallback


# ============================================================
# Agent 1：评论挖掘 Agent（ReviewMinerAgent）
# ============================================================
class ReviewMinerAgent:
    """
    评论挖掘 Agent
    从租客评论中提取六个维度的正面/负面关键词：隔音、采光、房东、水电、交通、安全
    """

    # 系统提示词：定义角色和分析框架
    SYSTEM_PROMPT = """你是一个专业的租房体验分析师。你的任务是分析租客评论，提取关键信息。

请从以下六个维度分析每条评论，提取正面和负面关键词：
1. 隔音（sound）：安静、噪音、隔音效果等
2. 采光（lighting）：朝向、采光、阳光、阴暗等
3. 房东（landlord）：态度、响应速度、是否好沟通等
4. 水电（utility）：水电费用、是否民用水电、费用是否合理等
5. 交通（transport）：地铁站距离、公交便利性、打车是否方便等
6. 安全（safety）：小区安全、门禁、周边环境、是否偏僻等

输出格式必须是严格的 JSON，不要有任何额外文字：
{"sound":{"positive":["关键词1","关键词2"],"negative":["关键词3"]}, "lighting":{...}, ...}"""

    # Few-shot 示例：帮助 AI 理解任务格式
    FEW_SHOT_EXAMPLE = """示例输入：
"房子朝南采光超好，白天完全不用开灯。但是晚上楼下大排档特别吵，一直闹到12点。房东人还不错，维修响应挺快的。离地铁站走路15分钟有点远。"

示例输出：
{"sound":{"positive":[],"negative":["楼下大排档吵","闹到12点"]},"lighting":{"positive":["朝南采光好","不用开灯"],"negative":[]},"landlord":{"positive":["人不错","维修响应快"],"negative":[]},"utility":{"positive":[],"negative":[]},"transport":{"positive":[],"negative":["离地铁站远","走路15分钟"]},"safety":{"positive":[],"negative":[]}}"""

    def mine(self, house_id):
        """
        分析指定房源的所有评论，提取多维度关键词

        参数：
            house_id (int): 房源ID

        返回：
            dict: 六维度关键词分析结果，格式见 SYSTEM_PROMPT
        """
        # --- 从数据库读取该房源所有评论 ---
        reviews = get_house_reviews(house_id)
        if not reviews:
            return {
                "sound": {"positive": [], "negative": []},
                "lighting": {"positive": [], "negative": []},
                "landlord": {"positive": [], "negative": []},
                "utility": {"positive": [], "negative": []},
                "transport": {"positive": [], "negative": []},
                "safety": {"positive": [], "negative": []},
            }

        # --- 拼接所有评论内容 ---
        review_texts = "\n---\n".join([f"[{r.platform}] 评分{r.rating}/5: {r.content}" for r in reviews])

        # --- 构建用户提示 ---
        user_prompt = f"{self.FEW_SHOT_EXAMPLE}\n\n现在请分析以下真实评论：\n{review_texts}"

        # --- 调用 DeepSeek API ---
        result_text = _call_deepseek(self.SYSTEM_PROMPT, user_prompt)

        # --- 解析返回的 JSON ---
        return _safe_json_parse(result_text, {
            "sound": {"positive": [], "negative": []},
            "lighting": {"positive": [], "negative": []},
            "landlord": {"positive": [], "negative": []},
            "utility": {"positive": [], "negative": []},
            "transport": {"positive": [], "negative": []},
            "safety": {"positive": [], "negative": []},
        })


# ============================================================
# Agent 2：房东风险评估 Agent（LandlordRiskAgent）
# ============================================================
class LandlordRiskAgent:
    """
    房东风险评估 Agent
    根据房东名下所有房源的评论，评估该房东是否存在押金不退、随意涨租等风险行为
    """

    # 系统提示词：定义风险评估框架
    SYSTEM_PROMPT = """你是一个租房风险调查员，专门识别不良房东和租赁纠纷风险。

请根据该房东所有房源的租客评论，判断是否存在以下风险：
1. 押金不退（deposit）：房东拒绝退还或克扣押金
2. 随意涨租（rent_hike）：合同期内或续租时无理涨租
3. 二房东转租（sublet）：非原房东、转租中间赚差价
4. 维修推诿（maintenance）：推卸维修责任、拖延处理
5. 态度恶劣（attitude）：沟通态度差、辱骂威胁等

输出格式必须是严格的 JSON：
{"risk_level":"高/中/低", "risk_items":[{"type":"风险类型","description":"具体风险描述及原文证据"}], "summary":"综合评估描述"}"""

    # 模拟降级数据（API 不可用时的备用方案）
    _FALLBACK_RESULT = {
        "risk_level": "低",
        "risk_items": [],
        "summary": "暂未发现明显风险（AI 分析未启用，请配置 DEEPSEEK_API_KEY 以获取详细分析）",
    }

    def assess(self, landlord_phone_hash):
        """
        评估指定房东的风险等级

        参数：
            landlord_phone_hash (str): 房东手机号哈希

        返回：
            dict: 风险评估结果
        """
        # --- 查出该房东的所有房源 ---
        houses = get_houses_by_landlord(landlord_phone_hash)
        if not houses:
            return {
                "risk_level": "低",
                "risk_items": [],
                "summary": "该房东暂无房源记录，无法评估",
            }

        # --- 收集该房东所有房源的评论 ---
        all_reviews = []
        for house in houses:
            reviews = get_house_reviews(house.id)
            all_reviews.extend(reviews)

        # --- 构建评论汇总文本 ---
        review_texts = "\n---\n".join([f"[房源{review.house_id}][{review.platform}]: {review.content}" for review in all_reviews])

        if not review_texts:
            return {
                "risk_level": "低",
                "risk_items": [],
                "summary": "该房东暂无租客评论，无法评估",
            }

        # --- 获取房东基本信息 ---
        landlord_info = get_landlord_by_phone(landlord_phone_hash)
        landlord_type = landlord_info.type if landlord_info else "未知"
        complaint_count = landlord_info.complaint_count if landlord_info else 0

        # --- 构建用户提示 ---
        user_prompt = f"""房东类型：{landlord_type}
历史投诉次数：{complaint_count}次

该房东名下所有房源的租客评论如下：
{review_texts}

请根据以上评论，分析该房东的风险情况并输出 JSON。"""

        result_text = _call_deepseek(self.SYSTEM_PROMPT, user_prompt)

        # --- 解析返回的 JSON ---
        if result_text:
            return _safe_json_parse(result_text, self._FALLBACK_RESULT)
        else:
            return {
                "risk_level": "低",
                "risk_items": [],
                "summary": "AI 分析未启用，请配置 DEEPSEEK_API_KEY 环境变量以启用风险评估功能",
            }


# ============================================================
# Agent 3：最终决策顾问 Agent（FinalAdvisorAgent）
# ============================================================
class FinalAdvisorAgent:
    """
    最终决策顾问 Agent
    综合分析光照、噪声、价格、评论和房东风险，给出租房最终建议
    """

    # 系统提示词：定义综合决策框架
    SYSTEM_PROMPT = """你是一个经验丰富的毕业生租房顾问，专门帮助应届生做出明智的租房决策。

你将收到以下信息：
- 光照评级和模拟日照时长
- 隔音/噪声评级和预计分贝
- 房屋价格及与市场价的偏离程度
- 租客评论挖掘结果（六维度正负面关键词）
- 房东风险评估结果

请综合考虑所有因素，输出以下 JSON：
{
  "decision": "推荐/可考虑/不推荐",
  "risk_level": "红/黄/绿",
  "summary": "150字以内的综合建议，语气温暖贴心",
  "highlights": ["优点1", "优点2"],
  "warnings": ["缺点1", "缺点2"]
}"""

    # 模拟降级数据
    _FALLBACK_RESULT = {
        "decision": "可考虑",
        "risk_level": "黄",
        "summary": "该房源物理条件和价格基本合理，建议实地看房后决定。AI 详细分析未启用。",
        "highlights": ["数据自动评估", "建议实地考察"],
        "warnings": ["AI 分析未启用", "请结合实际情况判断"],
    }

    def advise(self, light_score, noise_score, price_deviation, review_data, landlord_risk):
        """
        综合所有维度信息，给出最终租房决策建议

        参数：
            light_score (dict): 日照分析结果 {"hours": float, "level": str}
            noise_score (dict): 噪声分析结果 {"db": float, "level": str}
            price_deviation (dict): 价格偏离分析 {"market_price": int, "deviation": float, "is_reasonable": bool}
            review_data (dict): 评论挖掘结果（六维度关键词）
            landlord_risk (dict): 房东风险评估结果

        返回：
            dict: 综合决策建议
        """
        # --- 构建结构化的用户提示 ---
        user_prompt = f"""请综合分析以下广州房源信息并给出最终租房建议：

【物理环境】
- 光照：{light_score['level']}（日均 {light_score['hours']} 小时）
- 噪声：{noise_score['level']}（预计 {noise_score['db']} dB）

【价格分析】
- 该户型市场参考价：{price_deviation.get('market_price', 'N/A')} 元/月
- 价格偏离：{price_deviation.get('deviation', 0):.1%}
- 价格是否合理：{'是' if price_deviation.get('is_reasonable', True) else '否'}

【评论挖掘结果】
{json.dumps(review_data, ensure_ascii=False, indent=2)}

【房东风险评估】
- 风险等级：{landlord_risk.get('risk_level', '未知')}
- 风险点：{json.dumps(landlord_risk.get('risk_items', []), ensure_ascii=False)}
- 综合描述：{landlord_risk.get('summary', '无')}

请给出最终建议 JSON。"""

        result_text = _call_deepseek(self.SYSTEM_PROMPT, user_prompt)

        # --- 解析返回的 JSON ---
        if result_text:
            return _safe_json_parse(result_text, self._FALLBACK_RESULT)
        else:
            # --- 降级方案：基于规则给出基本判断 ---
            return self._fallback_advise(light_score, noise_score, price_deviation, review_data, landlord_risk)

    def _fallback_advise(self, light_score, noise_score, price_deviation, review_data, landlord_risk):
        """
        当 AI API 不可用时的基于规则的降级决策
        根据各项指标评分给出合理建议
        """
        score = 0
        highlights = []
        warnings = []

        # 光照评分贡献
        if light_score['level'] == "优":
            score += 25
            highlights.append(f"采光极佳（日均 {light_score['hours']} 小时）")
        elif light_score['level'] == "良":
            score += 18
            highlights.append(f"采光良好（日均 {light_score['hours']} 小时）")
        elif light_score['level'] == "差":
            score += 0
            warnings.append(f"采光较差（日均仅 {light_score['hours']} 小时）")
        else:
            score += 10

        # 噪声评分贡献
        if noise_score['level'] == "优":
            score += 25
            highlights.append(f"环境安静（预计 {noise_score['db']} dB）")
        elif noise_score['level'] == "良":
            score += 18
            highlights.append(f"噪声可控（预计 {noise_score['db']} dB）")
        elif noise_score['level'] == "差":
            score += 0
            warnings.append(f"噪声较大（预计 {noise_score['db']} dB）")
        else:
            score += 10

        # 价格合理性
        if price_deviation.get('is_reasonable', True):
            score += 25
        else:
            score += 10
            warnings.append("价格高于市场参考价，建议议价")

        # 房东风险
        risk_level = landlord_risk.get('risk_level', '低')
        if risk_level == "低":
            score += 25
        elif risk_level == "高":
            score += 0
            warnings.append(f"房东存在高风险：{landlord_risk.get('summary', '')}")
        else:
            score += 12

        # 综评决策
        if score >= 80:
            decision, risk = "推荐", "绿"
        elif score >= 50:
            decision, risk = "可考虑", "黄"
        else:
            decision, risk = "不推荐", "红"

        return {
            "decision": decision,
            "risk_level": risk,
            "summary": f"综合评估得分 {score}/100。{'该房源综合条件不错，值得推荐。' if decision == '推荐' else '该房源条件中等，建议实地考察后决定。' if decision == '可考虑' else '该房源存在较多问题，建议多看几家再做决定。'}",
            "highlights": highlights[:5],
            "warnings": warnings[:5],
        }
