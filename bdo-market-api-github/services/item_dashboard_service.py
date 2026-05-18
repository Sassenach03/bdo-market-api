from typing import Optional, List
import pandas as pd

from repository.item_history_repository import load_item_history
from utils.analysis_helpers import add_basic_indicators
from services.support_resistance_service import calculate_support_resistance
from services.forecast_service import calculate_forecast
from services.market_regime_service import calculate_market_regime


def _safe_float(value):
    if value is None:
        return None
    try:
        if pd.isna(value):
            return None
        return float(value)
    except Exception:
        return None


def _safe_iso_datetime(value) -> Optional[str]:
    try:
        if value is None or pd.isna(value):
            return None
        return pd.to_datetime(value).isoformat()
    except Exception:
        return None


def _get_rsi_state(rsi: Optional[float]) -> Optional[str]:
    if rsi is None:
        return None
    if rsi >= 70:
        return "overbought"
    if rsi <= 30:
        return "oversold"
    if rsi >= 60:
        return "bullish"
    if rsi <= 40:
        return "bearish"
    return "neutral"


def _get_macd_state(macd: Optional[float], macd_signal: Optional[float]) -> Optional[str]:
    if macd is None or macd_signal is None:
        return None
    if macd > macd_signal:
        return "bullish"
    if macd < macd_signal:
        return "bearish"
    return "neutral"


def _get_level_state(
    current_price: Optional[float],
    support_level: Optional[float],
    resistance_level: Optional[float],
    near_threshold: float = 0.03,
) -> Optional[str]:
    if current_price is None:
        return None

    near_support = False
    near_resistance = False

    if support_level not in (None, 0):
        near_support = abs(current_price - support_level) / support_level <= near_threshold

    if resistance_level not in (None, 0):
        near_resistance = abs(current_price - resistance_level) / resistance_level <= near_threshold

    if near_support:
        return "near_support"
    if near_resistance:
        return "near_resistance"
    if support_level is not None and resistance_level is not None:
        return "inside_range"
    return None


def _distance_pct(current_price: Optional[float], level: Optional[float]) -> Optional[float]:
    if current_price is None or level in (None, 0):
        return None
    return abs(current_price - level) / level


def _build_insights(
    latest_row,
    support_level: Optional[float],
    resistance_level: Optional[float],
    regime_data: dict,
    forecast_data: dict,
) -> List[str]:
    insights: List[str] = []

    current_price = _safe_float(latest_row.get("base_price"))
    ma7 = _safe_float(latest_row.get("ma7"))
    ma30 = _safe_float(latest_row.get("ma30"))
    rsi = _safe_float(latest_row.get("rsi"))
    macd = _safe_float(latest_row.get("macd"))
    macd_signal = _safe_float(latest_row.get("macd_signal"))
    volume_spike = _safe_float(latest_row.get("volume_spike"))

    market_regime = regime_data.get("market_regime")
    forecast_change_pct = forecast_data.get("forecast_change_pct")

    if current_price is not None and ma7 is not None and ma30 is not None:
        if current_price > ma7 and current_price > ma30:
            insights.append("The price is above the short-term and medium-term averages.")
        elif current_price < ma7 and current_price < ma30:
            insights.append("The price is below both major averages.")
        else:
            insights.append("The price is between averages, giving a mixed picture of the market.")

    if rsi is not None:
        if rsi >= 70:
            insights.append("RSI indicates an overbought zone.")
        elif rsi <= 30:
            insights.append("RSI indicates oversold zone.")
        else:
            insights.append("RSI remains in the neutral zone.")

    if macd is not None and macd_signal is not None:
        if macd > macd_signal:
            insights.append("MACD supports the upside scenario.")
        elif macd < macd_signal:
            insights.append("MACD supports a downside scenario.")

    if volume_spike is not None:
        if volume_spike >= 1.5:
            insights.append("The volume is clearly higher than the average.")
        elif volume_spike <= 0.7:
            insights.append("Volume is lower than typical levels.")

    dist_support = _distance_pct(current_price, support_level)
    dist_resistance = _distance_pct(current_price, resistance_level)

    if dist_support is not None and dist_support <= 0.03:
        insights.append("The price is close to support.")

    if dist_resistance is not None and dist_resistance <= 0.03:
        insights.append("The price is close to resistance.")

    if market_regime:
        insights.append(f"Dominant market condition: {market_regime}.")

    if forecast_change_pct is not None:
        if forecast_change_pct > 0.03:
            insights.append("Forecast suggests positive short-term potential.")
        elif forecast_change_pct < -0.03:
            insights.append("The forecast suggests a risk of further decline.")

    return insights[:6]


def _build_summary_text(
    latest_row,
    support_level: Optional[float],
    resistance_level: Optional[float],
    regime_data: dict,
    forecast_data: dict,
) -> str:
    parts: List[str] = []

    current_price = _safe_float(latest_row.get("base_price"))
    ma7 = _safe_float(latest_row.get("ma7"))
    ma30 = _safe_float(latest_row.get("ma30"))
    rsi = _safe_float(latest_row.get("rsi"))
    market_regime = regime_data.get("market_regime")
    forecast_change_pct = forecast_data.get("forecast_change_pct")

    if market_regime:
        parts.append(f"The market is currently classified as {market_regime}.")

    if current_price is not None and ma7 is not None and ma30 is not None:
        if current_price > ma7 > ma30:
            parts.append("The price remains above average, which supports the upward trend.")
        elif current_price < ma7 < ma30:
            parts.append("The price remains below averages, supporting the downward trend.")
        else:
            parts.append("The pattern of price relative to averages is mixed and does not give a clear signal.")

    if rsi is not None:
        if rsi >= 70:
            parts.append("RSI is high and may suggest overheating of the movement.")
        elif rsi <= 30:
            parts.append("RSI is low and may suggest oversold.")
        else:
            parts.append("RSI remains in the neutral range.")

    dist_support = _distance_pct(current_price, support_level)
    dist_resistance = _distance_pct(current_price, resistance_level)

    if dist_support is not None and dist_support <= 0.03:
        parts.append("The price is close to support.")
    elif dist_resistance is not None and dist_resistance <= 0.03:
        parts.append("The price is close to resistance.")
    elif support_level is not None and resistance_level is not None:
        parts.append("The price is moving within the main support-resistance range.")

    if forecast_change_pct is not None:
        if forecast_change_pct > 0:
            parts.append("The short-term forecast suggests possible further growth.")
        elif forecast_change_pct < 0:
            parts.append("The short-term forecast suggests possible further price weakness.")

    return " ".join(parts)


def build_item_dashboard(
    item_id: int,
    chart_limit: int = 90,
    forecast_days: int = 7,
    history_days: int = 90,
) -> dict:
    df = load_item_history(item_id=item_id)

    if df.empty:
        raise ValueError(f"No data found for item_id={item_id}")

    df = add_basic_indicators(df)
    latest = df.iloc[-1]

    levels_raw = calculate_support_resistance(item_id=item_id, recent_days=90)
    regime_raw = calculate_market_regime(item_id=item_id)
    forecast_raw = calculate_forecast(
        item_id=item_id,
        history_days=history_days,
        forecast_days=forecast_days,
    )

    support_level = _safe_float(levels_raw.get("support"))
    resistance_level = _safe_float(levels_raw.get("resistance"))
    current_price = _safe_float(latest.get("base_price"))

    distance_to_support_pct = _distance_pct(current_price, support_level)
    distance_to_resistance_pct = _distance_pct(current_price, resistance_level)

    rsi_value = _safe_float(latest.get("rsi"))
    macd_value = _safe_float(latest.get("macd"))
    macd_signal_value = _safe_float(latest.get("macd_signal"))

    regime_block = regime_raw.get("regime") or {}
    forecast_block = forecast_raw.get("forecast") or {}

    regime_data = {
        "market_regime": regime_block.get("code"),
        "label_pl": regime_block.get("label_pl"),
        "reason": regime_block.get("reason"),
        "confidence": None,
    }

    forecast_data = {
        "forecast_price": _safe_float(forecast_block.get("predicted_last_price")),
        "forecast_change_pct": _safe_float(forecast_block.get("predicted_change_pct")),
        "mae": _safe_float(forecast_block.get("mae")),
        "confidence": "medium",
    }

    chart_df = df.tail(chart_limit).copy()
    chart_series = []

    for _, row in chart_df.iterrows():
        chart_series.append({
            "recorded_at": _safe_iso_datetime(row.get("recorded_at")),
            "base_price": _safe_float(row.get("base_price")),
            "ma7": _safe_float(row.get("ma7")),
            "ma30": _safe_float(row.get("ma30")),
        })

    insights = _build_insights(
        latest_row=latest,
        support_level=support_level,
        resistance_level=resistance_level,
        regime_data=regime_data,
        forecast_data=forecast_data,
    )

    summary_text = _build_summary_text(
        latest_row=latest,
        support_level=support_level,
        resistance_level=resistance_level,
        regime_data=regime_data,
        forecast_data=forecast_data,
    )
    recommendation, recommendation_reason = _get_recommendation(
        latest_row=latest,
        support_level=support_level,
        resistance_level=resistance_level,
        regime_data=regime_data,
        forecast_data=forecast_data,
    )

    return {
        "item": {
            "item_id": item_id,
            "name": None,
        },
        "overview": {
            "current_price": current_price,
            "return_1d": _safe_float(latest.get("return_1d")),
            "return_7d": _safe_float(latest.get("return_7d")),
            "return_30d": _safe_float(latest.get("return_30d")),
            "volatility_7": _safe_float(latest.get("volatility_7")),
            "volatility_30": _safe_float(latest.get("volatility_30")),
            "liquidity_7d": _safe_float(latest.get("liquidity_7d")),
            "liquidity_30d": _safe_float(latest.get("liquidity_30d")),
            "volume_spike": _safe_float(latest.get("volume_spike")),
            "recorded_at": _safe_iso_datetime(latest.get("recorded_at")),
        },
        "indicators": {
            "ma7": _safe_float(latest.get("ma7")),
            "ma30": _safe_float(latest.get("ma30")),
            "ma7_slope": _safe_float(latest.get("ma7_slope")),
            "rsi": rsi_value,
            "rsi_state": _get_rsi_state(rsi_value),
            "macd": macd_value,
            "macd_signal": macd_signal_value,
            "macd_histogram": _safe_float(latest.get("macd_histogram")),
            "macd_state": _get_macd_state(macd_value, macd_signal_value),
            "price_position_30": _safe_float(latest.get("price_position_30")),
            "price_position_90": _safe_float(latest.get("price_position_90")),
        },
        "levels": {
            "support_level": support_level,
            "resistance_level": resistance_level,
            "distance_to_support_pct": distance_to_support_pct,
            "distance_to_resistance_pct": distance_to_resistance_pct,
            "level_state": _get_level_state(
                current_price=current_price,
                support_level=support_level,
                resistance_level=resistance_level,
            ),
        },
        "regime": regime_data,
        "forecast": forecast_data,
        "insights": insights,
        "summary_text": summary_text,
        "chart": chart_series,
        "recommendation": recommendation,
        "recommendation_reason": recommendation_reason,
    }
def _get_recommendation(
    latest_row,
    support_level: Optional[float],
    resistance_level: Optional[float],
    regime_data: dict,
    forecast_data: dict,
) -> tuple[str, str]:

    current_price = _safe_float(latest_row.get("base_price"))
    rsi = _safe_float(latest_row.get("rsi"))
    macd = _safe_float(latest_row.get("macd"))
    macd_signal = _safe_float(latest_row.get("macd_signal"))

    forecast_change = forecast_data.get("forecast_change_pct")
    regime = regime_data.get("market_regime")

    dist_support = _distance_pct(current_price, support_level)
    dist_resistance = _distance_pct(current_price, resistance_level)

    near_support = dist_support is not None and dist_support <= 0.03
    near_resistance = dist_resistance is not None and dist_resistance <= 0.03

    macd_bullish = macd is not None and macd_signal is not None and macd > macd_signal
    macd_bearish = macd is not None and macd_signal is not None and macd < macd_signal

    rsi_oversold = rsi is not None and rsi <= 30
    rsi_overbought = rsi is not None and rsi >= 70

    forecast_up = forecast_change is not None and forecast_change > 0.01
    forecast_down = forecast_change is not None and forecast_change < -0.01

    if near_support and macd_bullish and not rsi_overbought:
        return "buy", "Price at support + MACD bullish"
    if near_resistance and macd_bearish:
        return "sell", "CPrice at resistance + MACD down"
    if forecast_down and macd_bearish:
        return "sell", "Forecast and momentum indicate a decline"
    if near_support:
        return "watch_support", "Price is testing support"
    if near_resistance:
        return "watch_resistance", "Price close to resistance"
    if regime == "uptrend":
        return "watch", "Upward trend, no good entry"
    if regime == "downtrend":
        return "watch", "Downward trend, no good exit"
    return "watch", "No clear signal"



