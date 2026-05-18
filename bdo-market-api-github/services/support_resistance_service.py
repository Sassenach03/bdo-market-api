import numpy as np
import pandas as pd
from repository.item_history_repository import load_item_history
from utils.analysis_helpers import safe_round


def detect_support_resistance(df: pd.DataFrame, bins_count=12, recent_days=90):
    df_recent = df.tail(recent_days).copy()

    if df_recent.empty:
        return None, None, [], pd.DataFrame()

    df_recent["volume_ma7"] = df_recent["trade_volume"].rolling(7).mean()
    df_recent["volume_spike"] = df_recent["trade_volume"] / (df_recent["volume_ma7"] + 1)

    df_recent["future_price_3d"] = df_recent["base_price"].shift(-3)
    df_recent["future_price_change_3d"] = df_recent["future_price_3d"] - df_recent["base_price"]

    prices = df_recent["base_price"].dropna()

    if prices.empty:
        return None, None, [], pd.DataFrame()

    hist, bins = np.histogram(prices, bins=bins_count)
    top_idx = np.argsort(hist)[-4:]

    levels = []
    for idx in top_idx:
        low = bins[idx]
        high = bins[idx + 1]
        center = (low + high) / 2
        levels.append((round(low, 1), round(high, 1), round(center, 1)))

    spikes = df_recent[df_recent["volume_spike"] > 1].copy()
    events_analysis = []

    for _, row in spikes.iterrows():
        price = row["base_price"]
        date = row["recorded_at"]
        future_change = row["future_price_change_3d"]

        if pd.isna(future_change):
            continue

        for level in levels:
            low, high, center = level
            if low <= price <= high:
                events_analysis.append({
                    "date": date,
                    "price": price,
                    "zone_center": center,
                    "volume_spike": row["volume_spike"],
                    "future_price_change_3d": future_change
                })

    events_df = pd.DataFrame(events_analysis)

    if events_df.empty:
        return None, None, levels, events_df

    zone_stats = events_df.groupby("zone_center")["future_price_change_3d"].mean()
    zone_dict = zone_stats.to_dict()

    if len(zone_dict) < 2:
        only_level = list(zone_dict.keys())[0]
        return only_level, only_level, levels, events_df

    support_level = max(zone_dict, key=zone_dict.get)
    resistance_level = min(zone_dict, key=zone_dict.get)

    return support_level, resistance_level, levels, events_df


def calculate_support_resistance(
    item_id: int,
    from_date: str | None = None,
    to_date: str | None = None,
    bins_count: int = 12,
    recent_days: int = 90,
) -> dict:
    df = load_item_history(item_id=item_id, from_date=from_date, to_date=to_date)

    if df.empty:
        return {
            "item_id": item_id,
            "count": 0,
            "support": None,
            "resistance": None,
            "zones": [],
            "events": [],
        }

    support_level, resistance_level, levels, events_df = detect_support_resistance(
        df=df,
        bins_count=bins_count,
        recent_days=recent_days,
    )

    zones = [
        {
            "low": level[0],
            "high": level[1],
            "center": level[2],
        }
        for level in levels
    ]

    events = []
    if not events_df.empty:
        for _, row in events_df.iterrows():
            events.append({
                "date": row["date"].isoformat(),
                "price": safe_round(row["price"]),
                "zone_center": safe_round(row["zone_center"]),
                "volume_spike": safe_round(row["volume_spike"], 4),
                "future_price_change_3d": safe_round(row["future_price_change_3d"]),
            })

    return {
        "item_id": item_id,
        "count": len(df),
        "filters": {
            "from_date": from_date,
            "to_date": to_date,
            "bins_count": bins_count,
            "recent_days": recent_days,
        },
        "support": safe_round(support_level),
        "resistance": safe_round(resistance_level),
        "zones": zones,
        "events": events,
    }