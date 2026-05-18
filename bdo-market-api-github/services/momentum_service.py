from repository.item_history_repository import load_item_history
from utils.analysis_helpers import add_basic_indicators, safe_round


def calculate_momentum(
    item_id: int,
    from_date: str | None = None,
    to_date: str | None = None,
) -> dict:
    df = load_item_history(item_id=item_id, from_date=from_date, to_date=to_date)

    if df.empty:
        return {
            "item_id": item_id,
            "count": 0,
            "momentum": None,
            "filters": {
                "from_date": from_date,
                "to_date": to_date,
            }
        }

    df = add_basic_indicators(df)
    latest = df.iloc[-1]
    price_pos = latest["price_position_30"]
    if price_pos < 0.2:
        signal = "undervalued"
    elif price_pos > 0.8:
        signal = "overvalued"
    else:
        signal = "neutral"


    return {
        "item_id": item_id,
        "count": len(df),
        "filters": {
            "from_date": from_date,
            "to_date": to_date,
        },
        "momentum": {
            "current_price": safe_round(latest["base_price"]),
            "return_1d": safe_round(latest["return_1d"], 4),
            "return_7d": safe_round(latest["return_7d"], 4),
            "return_30d": safe_round(latest["return_30d"], 4),
            "return_90d": safe_round(latest["return_90d"], 4),
            "price_position_30": safe_round(latest["price_position_30"], 4),
            "price_position_90": safe_round(latest["price_position_90"], 4),
            "signal": signal,
        }
    }