from repository.item_history_repository import load_item_history
from services.support_resistance_service import detect_support_resistance
from utils.analysis_helpers import add_basic_indicators, safe_round
def interpret_rsi_with_levels(
        current_price : float,
        rsi_value: float,
        support_level : float | None,
        resistance_level : float | None,
        near_threshold : float = 0.1,
) -> dict:
    is_near_support = False
    is_near_resistance = False

    if support_level is not None and support_level != 0:
        is_near_support = abs(current_price - support_level) / support_level <= near_threshold
    if resistance_level is not None and resistance_level != 0:
        is_near_support = abs(current_price - resistance_level) / resistance_level <= near_threshold

        if rsi_value < 30 and is_near_support:
            return {
                "signal": "possible_rebound",
                "message": "The RSI indicates oversold and the price is close to support",
                "strength": "high",
                "is_near_support": is_near_support,
                "is_near_resistance": is_near_resistance,
            }
        if rsi_value > 70 and is_near_resistance:
            return {
                "signal": "possible_rejection",
                "message": "The RSI indicates overbuy and the price is close to resistance",
                "strength": "High",
                "is_near_resistance": is_near_resistance,
                "is_near_support": is_near_support,
            }
        if rsi_value < 30:
            return {
                "signal": "oversold",
                "message": "RSI indicates an oversold market, but the price is not directly at support",
                "strength": "medium",
                "is_near_support": is_near_support,
                "is_near_resistance": is_near_resistance,
            }
        if rsi_value > 70:
            return {
                "signal": "overbuy",
                "message": "The RSI indicates an overbought market, but the price is not directly at resistance.",
                "strength": "medium",
                "is_near_support": is_near_support,
                "is_near_resistance": is_near_resistance,

            }
        return {
            "signal": "neutral",
            "message": "RSI does not indicate an extreme market condition or the price is not at key levels",
            "strength": "low",
            "is_near_support": is_near_support,
            "is_near_resistance": is_near_resistance,
        }
def calculate_rsi_support_resistance(
    item_id: int,
    from_date: str | None = None,
    to_date: str | None = None,
    bins_count: int = 12,
    recent_days: int = 90,
    near_threshold: float = 0.03,
) -> dict:
    df = load_item_history(item_id=item_id, from_date=from_date, to_date=to_date)

    if df.empty:
        return {
            "item_id": item_id,
            "count": 0,
            "analysis": None,
            "reason": "brak danych dla podanego item_id",
        }

    df = add_basic_indicators(df)
    df_valid = df.dropna().copy()

    if df_valid.empty:
        return {
            "item_id": item_id,
            "count": len(df),
            "analysis": None,
            "reason": "brak wystarczających danych do policzenia RSI",
        }

    latest = df_valid.iloc[-1]

    support_level, resistance_level, _, _ = detect_support_resistance(
        df=df,
        bins_count=bins_count,
        recent_days=recent_days,
    )

    interpretation = interpret_rsi_with_levels(
        current_price=float(latest["base_price"]),
        rsi_value=float(latest["rsi_14"]),
        support_level=support_level,
        resistance_level=resistance_level,
        near_threshold=near_threshold,
    )

    return {
        "item_id": item_id,
        "count": len(df),
        "filters": {
            "from_date": from_date,
            "to_date": to_date,
            "bins_count": bins_count,
            "recent_days": recent_days,
            "near_threshold": near_threshold,
        },
        "analysis": {
            "recorded_at": latest["recorded_at"].isoformat(),
            "current_price": safe_round(latest["base_price"]),
            "rsi_14": safe_round(latest["rsi_14"], 2),
            "support": safe_round(support_level),
            "resistance": safe_round(resistance_level),
            "signal": interpretation["signal"],
            "message": interpretation["message"],
            "strength": interpretation["strength"],
            "is_near_support": interpretation["is_near_support"],
            "is_near_resistance": interpretation["is_near_resistance"],
        },
    }

