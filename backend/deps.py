"""FastAPI 依赖注入"""
from functools import lru_cache
from backend.agents import ReviewMinerAgent, LandlordRiskAgent, FinalAdvisorAgent


@lru_cache()
def get_agents():
    """返回三个 AI Agent 的单例实例（缓存，避免重复初始化）"""
    return {
        "miner": ReviewMinerAgent(),
        "risk": LandlordRiskAgent(),
        "advisor": FinalAdvisorAgent(),
    }
