import numpy as np
from statsmodels.tsa.holtwinters import Holt
from repository.item_history_repository import load_item_history
from utils.analysis_helpers import safe_round


def holt_forecast(prices, forecast_days=7):
    model = Holt(prices, initialization_method="estimated")
    fitted_model = model.fit(optimized=True)
    fitted_values = fitted_model.fittedvalues
    forecast_values = fitted_model.forecast(forecast_days)
    return fitted_model, fitted_values, forecast_values


def calculate_forecast(
    item_id: int,
    forecast_days: int = 5,
    history_days: int = 90,
    from_date: str | None = None,
    to_date: str | None = None,
) -> dict:
    df = load_item_history(item_id=item_id, from_date=from_date, to_date=to_date)

    if df.empty:
        return {
            "item_id": item_id,
            "count": 0,
            "forecast": None,
        }

    df = df.tail(history_days).copy().reset_index(drop=True)

    if len(df) < 10:
        return {
            "item_id": item_id,
            "count": len(df),
            "forecast": None,
            "reason": "za mało danych do prognozy Holt",
        }

    model, fitted_values, forecast_values = holt_forecast(
        df["base_price"],
        forecast_days=forecast_days,
    )

    current_price = df["base_price"].iloc[-1]
    predicted_last = forecast_values.iloc[-1]
    predicted_change = (predicted_last - current_price) / current_price
    mae = np.mean(np.abs(df["base_price"] - fitted_values))

    return {
        "item_id": item_id,
        "count": len(df),
        "filters": {
            "forecast_days": forecast_days,
            "history_days": history_days,
            "from_date": from_date,
            "to_date": to_date,
        },
        "forecast": {
            "current_price": safe_round(current_price),
            "predicted_last_price": safe_round(predicted_last),
            "predicted_change_pct": safe_round(predicted_change, 4),
            "mae": safe_round(mae),
            "series": [safe_round(x) for x in forecast_values.tolist()],
        }
    }