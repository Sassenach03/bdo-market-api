from repository.item_history_repository import load_item_history
from services.support_resistance_service import detect_support_resistance
from utils.analysis_helpers import add_basic_indicators, safe_round


REGIME_LABELS_PL = {
    "uptrend": "uptrend",
    "downtrend": "downtrend",
    "consolidation": "consolidation",
    "breakout_attempt": "breakout attempt",
    "panic_sell": "panic sell-off",
    "testing_resistance": "testing resistance",
    "weak_breakout_setup": "weak breakout setup",
    "bullish_transition": "bullish transition",
    "weak_rebound": "weak rebound",
    "testing_support": "testing support",
    "bearish_transition": "bearish transition",
    "support_breakdown": "support breakdown",
    "neutral": "neutral state"
}


def classify_market_regime_with_reason(row, support_level=None, resistance_level=None):
    price = row["base_price"]
    ma7 = row["ma7"]
    ma30 = row["ma30"]
    return_7d = row["return_7d"]
    ma7_slope = row["ma7_slope"]
    volatility_7 = row["volatility_7"]
    volatility_30 = row["volatility_30"]
    price_vs_ma30 = row["price_vs_ma30"]
    ma_gap = row["ma_gap"]
    volume_spike = row["volume_spike"]

    near_resistance = False
    near_support = False
    below_support = False
    above_resistance = False

    if resistance_level is not None and resistance_level != 0:
        near_resistance = abs(price - resistance_level) / resistance_level < 0.03
        above_resistance = price > resistance_level

    if support_level is not None and support_level != 0:
        near_support = abs(price - support_level) / support_level < 0.03
        below_support = price < support_level

    if (
        price < ma30
        and return_7d < -0.05
        and volume_spike > 1.3
        and volatility_7 > volatility_30 * 1.2
    ):
        return "panic_sell", "strong price decline, increased volume and increased volatility"

    if (
        price > ma30
        and return_7d > 0.03
        and ma7 > ma30
        and ma7_slope > 0
        and volume_spike > 1.2
        and (near_resistance or above_resistance)
    ):
        return "breakout_attempt", "The price is rising on increased volume and is attacking the resistance zone"

    if (
        price > ma30
        and ma7 > ma30
        and ma7_slope > 0
        and return_7d > 0
    ):
        return "uptrend", "The price remains above the 30-day average and the short-term trend is rising"

    if (
        price < ma30
        and ma7 < ma30
        and ma7_slope < 0
        and return_7d < 0
    ):
        return "downtrend", "price remains below the 30-day average and the short-term trend is down"

    if (
        abs(price_vs_ma30) < 0.03
        and abs(ma_gap) < 0.02
        and volatility_7 <= volatility_30 * 1.1
        and volume_spike < 1.2
    ):
        return "consolidation", "the price is moving close to the average and the market has no clear direction"

    if (
        price > ma30
        and return_7d > 0
        and near_resistance
        and volume_spike < 1.0
    ):
        return "testing_resistance", "the price has reached close to resistance, but the move is not confirmed by volume"

    if (
        price > ma30
        and return_7d > 0.02
        and near_resistance
        and ma7_slope <= 0
    ):
        return "weak_breakout_setup", "The price is near resistance, but short-term momentum is weakening."

    if (
        price > ma30
        and return_7d > 0
        and ma7 < ma30
    ):
        return "bullish_transition", "The price is improving relative to the 30-day average, but the short-term trend does not yet confirm full gains"

    if (
        price < ma30
        and return_7d > 0
        and ma7_slope > 0
    ):
        return "weak_rebound", "a price rebound is visible, but the market remains below the 30-day average"

    if (
        price < ma30
        and return_7d < 0
        and near_support
        and volume_spike < 1.0
    ):
        return "testing_support", "the price has approached support, but the decline is not confirmed by strong volume"

    if (
        price < ma30
        and return_7d < 0
        and ma7 > ma30
    ):
        return "bearish_transition", "The price has weakened below the 30-day moving average, but the previous trend has not yet been completely reversed."

    if below_support and return_7d < 0:
        return "support_breakdown", "the price has fallen below support, which may indicate further downward pressure"

    return "neutral", "the signals are mixed and do not indicate a clear market condition"


def calculate_market_regime(
    item_id: int,
    from_date: str | None = None,
    to_date: str | None = None,
) -> dict:
    df = load_item_history(item_id=item_id, from_date=from_date, to_date=to_date)

    if df.empty:
        return {
            "item_id": item_id,
            "count": 0,
            "regime": None,
        }

    df = add_basic_indicators(df)
    support_level, resistance_level, _, _ = detect_support_resistance(df)

    df_valid = df.dropna().copy()
    if df_valid.empty:
        return {
            "item_id": item_id,
            "count": len(df),
            "regime": None,
            "reason": "insufficient data to classify the market",
        }

    latest = df_valid.iloc[-1]
    regime_code, regime_reason = classify_market_regime_with_reason(
        latest,
        support_level=support_level,
        resistance_level=resistance_level,
    )

    return {
        "item_id": item_id,
        "count": len(df),
        "filters": {
            "from_date": from_date,
            "to_date": to_date,
        },
        "latest": {
            "recorded_at": latest["recorded_at"].isoformat(),
            "base_price": safe_round(latest["base_price"]),
            "ma7": safe_round(latest["ma7"]),
            "ma30": safe_round(latest["ma30"]),
            "return_7d": safe_round(latest["return_7d"], 4),
            "volatility_7": safe_round(latest["volatility_7"], 4),
            "volatility_30": safe_round(latest["volatility_30"], 4),
            "volume_spike": safe_round(latest["volume_spike"], 4),
        },
        "support": safe_round(support_level),
        "resistance": safe_round(resistance_level),
        "regime": {
            "code": regime_code,
            "label_pl": REGIME_LABELS_PL.get(regime_code, regime_code),
            "reason": regime_reason,
        },
    }