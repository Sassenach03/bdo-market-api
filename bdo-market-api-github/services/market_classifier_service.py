

def get_trend_strength_label(trend_strength: float) -> str:
    if trend_strength < 0.001:
        return "very_weak"
    if trend_strength < 0.003:
        return "weak"
    if trend_strength < 0.007:
        return "medium"
    return "strong"


def get_trend_quality_label(trend_r2: float) -> str:
    if trend_r2 < 0.2:
        return "noisy"
    if trend_r2 < 0.5:
        return "mixed"
    if trend_r2 < 0.75:
        return "fairly_clean"
    return "clean"


def classify_market(features: dict) -> dict:
    slope = features["trend_slope"]
    volatility = features["volatility"]
    efficiency = features["efficiency_ratio"]
    cross = features["ma_cross_count"]
    trend_strength = features["trend_strength"]
    trend_r2 = features["trend_r2"]

    if abs(slope) > 50 and trend_strength > 0.0008 and trend_r2 > 0.3:
        if slope > 0:
            market_type = "uptrend"
        else:
            market_type = "downtrend"


    elif efficiency < 0.15 and cross > 6:
        market_type = "sideways"


    elif volatility > 0.05 and efficiency < 0.2:
        market_type = "chaotic"

    else:
        market_type = "neutral"

    return {
        "type": market_type,
        "trend_strength_label": get_trend_strength_label(trend_strength),
        "trend_quality_label": get_trend_quality_label(trend_r2),
    }