from repository.item_history_repository import load_item_history
from utils.analysis_helpers import add_basic_indicators, safe_round

def calculate_bolling_bands(
        item_id: int,
        limit: int | None = None,
        from_date: str | None = None,
        to_date: str | None = None
) -> dict:
    df = load_item_history(item_id=item_id, from_date=from_date, to_date=to_date)
    if df.empty:
        return {
            "item_id": item_id,
            "count": 0,
            "filters": {
                "limit": limit,
                "from_date": from_date,
                "to_date": to_date,
            },
            "series": []
        }
    prices = df["base_price"]
    middle_band = prices.rolling(window=20).mean()
    rolling_std = prices.rolling(window=20).std(ddof=0)
    upper_band = middle_band + 2  * rolling_std
    lower_band = middle_band - 2 * rolling_std
    result_df = df[["recorded_at", "base_price"]].copy()
    result_df["bb_middle"] = middle_band
    result_df["bb_upper"] = upper_band
    result_df["bb_lower"] = lower_band
    if limit is not None and limit > 0:
        result_df = result_df.tail(limit).reset_index(drop=True)
    series = []
    for _, row in result_df.iterrows():
        row_dict = {
            "recorded_at": row["recorded_at"].isoformat(),
            "base_price": safe_round(row["base_price"], 2),
            "bb_middle": safe_round(row["bb_middle"], 2),
            "bb_upper": safe_round(row["bb_upper"], 2),
            "bb_lower": safe_round(row["bb_lower"], 2),
        }
        series.append(row_dict)
        return {
            "item_id": item_id,
            "count": len(series),
            "filters": {
                "limit": limit,
                "from_date": from_date,
                "to_date": to_date,
            },
            "series": series
        }