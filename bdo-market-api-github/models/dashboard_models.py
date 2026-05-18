from typing import List, Optional
from pydantic import BaseModel


class DashboardItemInfo(BaseModel):
    item_id: int
    name: Optional[str] = None


class DashboardOverview(BaseModel):
    current_price: Optional[float] = None
    return_1d: Optional[float] = None
    return_7d: Optional[float] = None
    return_30d: Optional[float] = None
    volatility_7: Optional[float] = None
    volatility_30: Optional[float] = None
    liquidity_7d: Optional[float] = None
    liquidity_30d: Optional[float] = None
    volume_spike: Optional[float] = None
    recorded_at: Optional[str] = None


class DashboardIndicators(BaseModel):
    ma7: Optional[float] = None
    ma30: Optional[float] = None
    ma7_slope: Optional[float] = None
    rsi: Optional[float] = None
    rsi_state: Optional[str] = None
    macd: Optional[float] = None
    macd_signal: Optional[float] = None
    macd_histogram: Optional[float] = None
    macd_state: Optional[str] = None
    price_position_30: Optional[float] = None
    price_position_90: Optional[float] = None


class DashboardLevels(BaseModel):
    support_level: Optional[float] = None
    resistance_level: Optional[float] = None
    distance_to_support_pct: Optional[float] = None
    distance_to_resistance_pct: Optional[float] = None
    level_state: Optional[str] = None


class DashboardRegime(BaseModel):
    market_regime: Optional[str] = None
    label_pl: Optional[str] = None
    reason: Optional[str] = None
    confidence: Optional[str] = None


class DashboardForecast(BaseModel):
    forecast_price: Optional[float] = None
    forecast_change_pct: Optional[float] = None
    mae: Optional[float] = None
    confidence: Optional[str] = None


class DashboardChartPoint(BaseModel):
    recorded_at: Optional[str] = None
    base_price: Optional[float] = None
    ma7: Optional[float] = None
    ma30: Optional[float] = None


class DashboardResponse(BaseModel):
    item: DashboardItemInfo
    overview: DashboardOverview
    indicators: DashboardIndicators
    levels: DashboardLevels
    regime: DashboardRegime
    forecast: DashboardForecast
    insights: List[str]
    summary_text: str
    chart: List[DashboardChartPoint]
    recommendation: str
    recommendation_reason: str