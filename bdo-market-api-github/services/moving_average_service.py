from repository.item_history_repository import load_item_history


def calculate_moving_average(
    item_id: int,
    windows: list[int],
    limit: int | None = None,
    from_date: str | None = None,
    to_date: str | None = None,
) -> dict:
    df = load_item_history(
        item_id=item_id,
        from_date=from_date,
        to_date=to_date,
    )

    if df.empty:
        return {
            "item_id": item_id,
            "windows": windows,
            "count": 0,
            "series": []
        }

    result_df = df[["recorded_at", "base_price"]].copy()

    for window in windows:
        result_df[f"ma_{window}"] = result_df["base_price"].rolling(window=window).mean()

    if limit is not None and limit > 0:
        result_df = result_df.tail(limit).reset_index(drop=True)

    series = []

    for _, row in result_df.iterrows():
        row_dict = {
            "recorded_at": row["recorded_at"].isoformat(),
            "base_price": round(float(row["base_price"]), 2),
        }

        for window in windows:
            value = row[f"ma_{window}"]
            row_dict[f"ma_{window}"] = None if value != value else round(float(value), 2)

        series.append(row_dict)

    return {
        "item_id": item_id,
        "windows": windows,
        "count": len(series),
        "filters": {
            "limit": limit,
            "from_date": from_date,
            "to_date": to_date,
        },
        "series": series
    }