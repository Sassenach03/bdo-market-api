from repository.item_history_repository import load_item_history
from utils.analysis_helpers import (
    min_max_normalize,
    calculate_lagged_correlation,
    calculate_lag_range_correlations,
    find_best_lag,
    safe_round,
)
ALLOWED_METRICS = {
    "base_price",
    "trade_volume",
    "current_stock",
}
def calculate_item_to_item_correlation(
    item_a_id: int,
    item_b_id: int,
    metric: str = "base_price",
    max_lag: int = 10,
    limit: int | None = 200,
    from_date: str | None = None,
    to_date: str | None = None,
) -> dict:
    if metric not in ALLOWED_METRICS:
        return {
            "item_a_id": item_a_id,
            "item_b_id": item_b_id,
            "analysis": None,
            "reason": f"Unsupported metric: {metric}",
        }

    if item_a_id == item_b_id:
        return {
            "item_a_id": item_a_id,
            "item_b_id": item_b_id,
            "analysis": None,
            "reason": "item_a_id and item_b_id must be different",
        }

    df_a = load_item_history(
        item_id=item_a_id,
        from_date=from_date,
        to_date=to_date,
    )

    df_b = load_item_history(
        item_id=item_b_id,
        from_date=from_date,
        to_date=to_date,
    )

    if df_a.empty or df_b.empty:
        return {
            "item_a_id": item_a_id,
            "item_b_id": item_b_id,
            "analysis": None,
            "reason": "no data for one or both items",
        }

    df_a = df_a[["recorded_at", metric]].copy()
    df_b = df_b[["recorded_at", metric]].copy()

    df_a = df_a.rename(columns={metric: "item_a_value"})
    df_b = df_b.rename(columns={metric: "item_b_value"})
    merged_df = df_a.merge(df_b, on="recorded_at", how="inner")
    merged_df = merged_df.dropna().sort_values("recorded_at").reset_index(drop=True)

    if limit is not None and limit > 0:
        merged_df = merged_df.tail(limit).reset_index(drop=True)

    if len(merged_df) < 3:
        return {
            "item_a_id": item_a_id,
            "item_b_id": item_b_id,
            "analysis": None,
            "reason": "too few common time points to calculate correlations",
        }
    correlation_now = calculate_lagged_correlation(
        series_a=merged_df["item_a_value"],
        series_b=merged_df["item_b_value"],
        lag=0,
    )

    lag_results = calculate_lag_range_correlations(
        series_a=merged_df["item_a_value"],
        series_b=merged_df["item_b_value"],
        max_lag=max_lag,
    )

    best_lag, best_lag_correlation = find_best_lag(lag_results)
    merged_df["item_a_normalized"] = min_max_normalize(merged_df["item_a_value"])
    merged_df["item_b_normalized"] = min_max_normalize(merged_df["item_b_value"])

    overlay_series = []
    for _, row in merged_df.iterrows():
        overlay_series.append({
            "recorded_at": row["recorded_at"].isoformat(),
            "item_a_raw": safe_round(row["item_a_value"], 4),
            "item_b_raw": safe_round(row["item_b_value"], 4),
            "item_a_normalized": safe_round(row["item_a_normalized"], 4),
            "item_b_normalized": safe_round(row["item_b_normalized"], 4),
        })
    interpretation = "Brak interpretacji."
    relationship = "unknown"

    if best_lag_correlation is not None:
        if best_lag_correlation >= 0.7:
            interpretation = "silna dodatnia korelacja"
            relationship = "positive"
        elif best_lag_correlation >= 0.4:
            interpretation = "umiarkowana dodatnia korelacja"
            relationship = "positive"
        elif best_lag_correlation <= -0.7:
            interpretation = "silna ujemna korelacja"
            relationship = "negative"
        elif best_lag_correlation <= -0.4:
            interpretation = "umiarkowana ujemna korelacja"
            relationship = "negative"
        else:
            interpretation = "słaba korelacja"
            relationship = "weak"
    return {
        "item_a_id": item_a_id,
        "item_b_id": item_b_id,
        "metric": metric,
        "count": len(merged_df),
        "filters": {
            "max_lag": max_lag,
            "limit": limit,
            "from_date": from_date,
            "to_date": to_date,
        },
        "analysis": {
            "correlation_now": safe_round(correlation_now, 4),
            "best_lag": best_lag,
            "best_lag_correlation": safe_round(best_lag_correlation, 4),
            "interpretation": interpretation,
            "relationship": relationship,
        },
        "lag_results": lag_results,
        "overlay_series": overlay_series,
    }