from repository.item_history_repository import load_item_history
from utils.analysis_helpers import add_basic_indicators, safe_round

def calculate_macd_analysis(
        item_id: int,
        limit: int | None = None,
        from_date: str | None = None,
        to_date: str | None = None,
) -> dict:
    df = load_item_history(item_id=item_id, from_date=from_date, to_date=to_date)
    if df.empty:
        return {
            "item_id": item_id,
            "count": 0,
            "series": [],
            "latest": None,
            "reason": "No data for this item_id"
        }
    df = add_basic_indicators(df)

    result_df = df[[
        "recorded_at",
        "base_price",
        "macd",
        "macd_signal",
        "macd_histogram",
    ]].copy()

    if limit is not None and limit > 0:
        result_df = result_df.tail(limit).reset_index(drop=True)
    series = []

    for _, row in result_df.iterrows():
        series.append({
        "recorded_at": row["recorded_at"].isoformat(),
        "base_price": safe_round(row["base_price"]),
        "macd": safe_round(row["macd"], 4),
        "signal": safe_round(row["macd_signal"], 4),
        "histogram": safe_round(row["macd_histogram"], 4),
        })

    latest_valid = result_df.dropna()
    lastest = None

    if not latest_valid.empty:
        last_row = latest_valid.iloc[-1]
        signal_type = "neutral"
        message = "No clear signal"

        if last_row["macd"] > last_row["macd_signal"]:
            signal_type = "bullish_momentum"
            message = "Linia MACD znajduje się powyżej linii sygnałowej, co wskazuje na przewagę momentum wzrostowego."
        elif last_row["macd"] < last_row["macd_signal"]:
            signal_type = "bearish_momentum"
            message = "Linia MACD znajduje się poniżej linii sygnałowej, co wskazuje na przewagę momentum spadkowego."

        latest = {
            "recorded_at": last_row["recorded_at"].isoformat(),
            "base_price": safe_round(last_row["base_price"]),
            "macd": safe_round(last_row["macd"], 4),
            "signal": safe_round(last_row["macd_signal"], 4),
            "histogram": safe_round(last_row["macd_histogram"], 4),
            "signal_type": signal_type,
            "message": message,
        }

        return {
            "item_id": item_id,
            "count": len(result_df),
            "filters": {
                "limit": limit,
                "from_date": from_date,
                "to_date": to_date,
            },
            "latest": latest,
            "series": series,
        }