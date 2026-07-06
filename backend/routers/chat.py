"""AI 对话助手 API"""
from fastapi import APIRouter
from pydantic import BaseModel
from openai import OpenAI
from backend.config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, DEEPSEEK_MODEL

router = APIRouter(prefix="/api/v1/chat", tags=["chat"])

SYSTEM_PROMPT = """你是"安租"的 AI 助手，帮助广州租房用户分析房源风险。

你的能力：
1. 解析用户输入的房源信息（链接、小区名、地址等），提取关键信息
2. 根据已有的房源数据分析日照、噪音、房东风险、价格合理性
3. 提供租房建议：怎么看房、怎么和房东沟通、怎么检查合同
4. 解释风险评估结果：什么是中/高风险，需要注意什么
5. 回答广州各区域租房市场行情

请用中文回答，回答简洁实用，每次控制在 200 字以内。"""


class ChatRequest(BaseModel):
    message: str
    history: list[dict] = []


class ChatResponse(BaseModel):
    reply: str


@router.post("", response_model=ChatResponse)
def chat(req: ChatRequest):
    if not DEEPSEEK_API_KEY:
        return ChatResponse(reply="AI 助手暂未配置（需要 DEEPSEEK_API_KEY）。\n你可以浏览房源数据或手动创建评估来分析风险。")

    client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for h in req.history[-10:]:
        messages.append(h)
    messages.append({"role": "user", "content": req.message})

    try:
        resp = client.chat.completions.create(model=DEEPSEEK_MODEL, messages=messages, max_tokens=500, temperature=0.7)
        return ChatResponse(reply=resp.choices[0].message.content)
    except Exception as e:
        return ChatResponse(reply=f"抱歉，AI 服务暂时不可用：{str(e)[:100]}")
