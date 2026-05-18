def select_algorithms(market_type: str) -> list[str]:
    if market_type in ["uptrend", "downtrend"]:
        return ["moving_average", "macd", "breakout"]

    if market_type == "sideways":
        return ["rsi", "bollinger_bands", "support_resistance"]

    if market_type == "chaotic":
        return ["volatility", "anomaly_detection"]

    return ["basic_analysis"]