from repository.item_all_history_repository import load_all_items_history_last_days


def calculate_moving_average_for_all_items(
    windows: list[int],
    days: int = 30,
    limit_per_item: int | None = None,
) -> dict:
    df = load_all_items_history_last_days(days=days)

    if df.empty:
        return {
            "windows": windows,
            "days": days,
            "count_items": 0,
            "items": []
        }

    df = df.sort_values(["item_id", "recorded_at"]).reset_index(drop=True)

    result_df = df[["item_id", "recorded_at", "base_price"]].copy()

    for window in windows:
        result_df[f"ma_{window}"] = (
            result_df.groupby("item_id")["base_price"]
            .transform(lambda s: s.rolling(window=window).mean())
        )

    items = []

    for item_id, group in result_df.groupby("item_id"):
        group = group.sort_values("recorded_at")

        if limit_per_item is not None and limit_per_item > 0:
            group = group.tail(limit_per_item)

        series = []

        for _, row in group.iterrows():
            row_dict = {
                "recorded_at": row["recorded_at"].isoformat(),
                "base_price": round(float(row["base_price"]), 2),
            }

            for window in windows:
                value = row[f"ma_{window}"]
                row_dict[f"ma_{window}"] = None if value != value else round(float(value), 2)

            series.append(row_dict)

        items.append({
            "item_id": int(item_id),
            "count": len(series),
            "series": series
        })

    return {
        "windows": windows,
        "days": days,
        "count_items": len(items),
        "items": items
    }