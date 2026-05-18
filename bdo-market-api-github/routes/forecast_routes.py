from fastapi import APIRouter, Query
from services.forecast_service import calculate_forecast

router = APIRouter()


@router.get("/api/items/{item_id}/forecast")
def get_forecast(
    item_id: int,
    forecast_days: int = Query(default=5, ge=1, le=30),
    history_days: int = Query(default=90, ge=10, le=365),
    from_date: str | None = Query(default=None),
    to_date: str | None = Query(default=None),
):
    return calculate_forecast(
        item_id=item_id,
        forecast_days=forecast_days,
        history_days=history_days,
        from_date=from_date,
        to_date=to_date,
    )