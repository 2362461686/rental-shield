"""服务层：整合 AI Agent 调用"""
import json
import config
from backend import agents as agent_module


def run_review_mining(house_id: int) -> dict:
    """对指定房源执行评论挖掘"""
    miner = agent_module.ReviewMinerAgent()
    return miner.mine(house_id)


def run_landlord_risk(phone_hash: str) -> dict:
    """对指定房东执行风险评估"""
    checker = agent_module.LandlordRiskAgent()
    return checker.assess(phone_hash)


def run_final_advice(light: dict, noise: dict, price_info: dict, review_data: dict, landlord_risk: dict) -> dict:
    """执行综合决策建议"""
    advisor = agent_module.FinalAdvisorAgent()
    return advisor.advise(light, noise, price_info, review_data, landlord_risk)
