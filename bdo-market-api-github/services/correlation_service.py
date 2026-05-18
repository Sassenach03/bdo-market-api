from repository.item_history_repository import load_item_history
from utils.analysis_helpers import (
    min_max_normalize,
    calculate_lagged_correlation,
    calculate_lag_range_correlations,
    find_best_lag,
    safe_round,
)


ALLOWED_SERIES = {
    "base_price",
    "trade_volume",
    "current_stock",
}
def calculate_series_correlation(
    item_id: int,
    series_a_name: str,
    series_b_name: str,
    max_lag: int = 10,
    limit: int | None = 200,
    from_date: str | None = None,
    to_date: str | None = None,
) -> dict:
    if series_a_name not in ALLOWED_SERIES:
        return {
            "item_id": item_id,
            "analysis": None,
            "reason": f"Nieobsługiwana seria_a: {series_a_name}",
        }

    if series_b_name not in ALLOWED_SERIES:
        return {
            "item_id": item_id,
            "analysis": None,
            "reason": f"Nieobsługiwana seria_b: {series_b_name}",
        }

    if series_a_name == series_b_name:
        return {
            "item_id": item_id,
            "analysis": None,
            "reason": "serie_a i seria_b muszą być różne",
        }

    df = load_item_history(
        item_id=item_id,
        from_date=from_date,
        to_date=to_date,
    )

    if df.empty:
        return {
            "item_id": item_id,
            "analysis": None,
            "reason": "brak danych dla podanego item_id",
        }

    result_df = df[["recorded_at", series_a_name, series_b_name]].copy()
    result_df = result_df.dropna().reset_index(drop=True)

    if limit is not None and limit > 0:
        result_df = result_df.tail(limit).reset_index(drop=True)

    if len(result_df) < 3:
        return {
            "item_id": item_id,
            "analysis": None,
            "reason": "za mało danych do policzenia korelacji",
        }

    correlation_now = calculate_lagged_correlation(
        series_a=result_df[series_a_name],
        series_b=result_df[series_b_name],
        lag=0,
    )

    lag_results = calculate_lag_range_correlations(
        series_a=result_df[series_a_name],
        series_b=result_df[series_b_name],
        max_lag=max_lag,
    )

    best_lag, best_lag_correlation = find_best_lag(lag_results)

    result_df["series_a_normalized"] = min_max_normalize(result_df[series_a_name])
    result_df["series_b_normalized"] = min_max_normalize(result_df[series_b_name])

    overlay_series = []
    for _, row in result_df.iterrows():
        overlay_series.append({
            "recorded_at": row["recorded_at"].isoformat(),
            "series_a_raw": safe_round(row[series_a_name], 4),
            "series_b_raw": safe_round(row[series_b_name], 4),
            "series_a_normalized": safe_round(row["series_a_normalized"], 4),
            "series_b_normalized": safe_round(row["series_b_normalized"], 4),
        })

    interpretation = "Brak interpretacji."
    if best_lag_correlation is not None:
        if best_lag_correlation >= 0.7:
            interpretation = "silna dodatnia korelacja"
        elif best_lag_correlation >= 0.4:
            interpretation = "umiarkowana dodatnia korelacja"
        elif best_lag_correlation <= -0.7:
            interpretation = "silna ujemna korelacja"
        elif best_lag_correlation <= -0.4:
            interpretation = "umiarkowana ujemna korelacja"
        else:
            interpretation = "słaba korelacja"

    return {
        "item_id": item_id,
        "count": len(result_df),
        "filters": {
            "series_a": series_a_name,
            "series_b": series_b_name,
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
        },
        "lag_results": lag_results,
        "overlay_series": overlay_series,
    }