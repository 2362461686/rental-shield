"""分析相关 Pydantic schemas"""
from pydantic import BaseModel
from typing import Optional


class SunlightResult(BaseModel):
    hours: float
    level: str


class NoiseResult(BaseModel):
    db: float
    level: str


class PriceAnalysis(BaseModel):
    market_price: int
    deviation: float
    is_reasonable: bool


class ReviewDimension(BaseModel):
    positive: list[str] = []
    negative: list[str] = []


class ReviewMiningResult(BaseModel):
    sound: ReviewDimension = ReviewDimension()
    lighting: ReviewDimension = ReviewDimension()
    landlord: ReviewDimension = ReviewDimension()
    utility: ReviewDimension = ReviewDimension()
    transport: ReviewDimension = ReviewDimension()
    safety: ReviewDimension = ReviewDimension()


class LandlordRiskResult(BaseModel):
    risk_level: str
    risk_items: list[dict] = []
    summary: str


class AdviceResult(BaseModel):
    decision: str
    risk_level: str
    summary: str
    highlights: list[str] = []
    warnings: list[str] = []


class FullAnalysisResponse(BaseModel):
    sunlight: SunlightResult
    noise: NoiseResult
    price_analysis: PriceAnalysis
    review_mining: ReviewMiningResult
    landlord_risk: LandlordRiskResult
    final_advice: AdviceResult
