from repository.item_history_repository import load_item_history
from services.support_resistance_service import detect_support_resistance
from services.market_regime_service import classify_market_regime_with_reason, REGIME_LABELS_PL
from services.forecast_service import holt_forecast
from utils.analysis_helpers import add_basic_indicators, safe_round
import numpy as np


def calculate_summary(
    item_id: int,
    from_date: str | None = None,
    to_date: str | None = None,
) -> dict:
    df = load_item_history(item_id=item_id, from_date=from_date, to_date=to_date)

    if df.empty:
        return {
            "item_id": item_id,
            "count": 0,
            "summary": None,
        }

    df = add_basic_indicators(df)
    support_level, resistance_level, _, _ = detect_support_resistance(df)

    df_valid = df.dropna().copy()
    latest = df.iloc[-1]

    regime = None
    if not df_valid.empty:
        latest_valid = df_valid.iloc[-1]
        regime_code, regime_reason = classify_market_regime_with_reason(
            latest_valid,
            support_level=support_level,
            resistance_level=resistance_level,
        )
        regime = {
            "code": regime_code,
            "label_pl": REGIME_LABELS_PL.get(regime_code, regime_code),
            "reason": regime_reason,
        }

    forecast = None
    df_forecast = df.tail(90).copy().reset_index(drop=True)
    if len(df_forecast) >= 10:
        _, fitted, pred = holt_forecast(df_forecast["base_price"], forecast_days=5)
        current_price = df_forecast["base_price"].iloc[-1]
        predicted_last = pred.iloc[-1]
        forecast = {
            "current_price": safe_round(current_price),
            "predicted_last_price": safe_round(predicted_last),
            "predicted_change_pct": safe_round((predicted_last - current_price) / current_price, 4),
            "mae": safe_round(np.mean(np.abs(df_forecast["base_price"] - fitted))),
        }

    return {
        "item_id": item_id,
        "count": len(df),
        "filters": {
            "from_date": from_date,
            "to_date": to_date,
        },
        "summary": {
            "recorded_at": latest["recorded_at"].isoformat(),
            "current_price": safe_round(latest["base_price"]),
            "ma7": safe_round(latest["ma7"]),
            "ma30": safe_round(latest["ma30"]),
            "return_1d": safe_round(latest["return_1d"], 4),
            "return_7d": safe_round(latest["return_7d"], 4),
            "return_30d": safe_round(latest["return_30d"], 4),
            "return_90d": safe_round(latest["return_90d"], 4),
            "volatility_7": safe_round(latest["volatility_7"], 4),
            "volatility_30": safe_round(latest["volatility_30"], 4),
            "liquidity_7d": safe_round(latest["liquidity_7d"]),
            "liquidity_30d": safe_round(latest["liquidity_30d"]),
            "support": safe_round(support_level),
            "resistance": safe_round(resistance_level),
            "market_regime": regime,
            "forecast": forecast,
        }
    }