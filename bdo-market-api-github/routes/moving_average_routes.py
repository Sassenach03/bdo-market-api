from fastapi import APIRouter, Query
from services.moving_average_service import calculate_moving_average

router = APIRouter()


@router.get("/api/items/{item_id}/moving-averages")
def get_moving_averages(
    item_id: int,
    windows: str = Query("7,30", description="Np. 7,30"),
    limit: int | None = Query(None, description="Zwróć tylko ostatnie N rekordów"),
    from_date: str | None = Query(None, description="Np. 2026-01-01"),
    to_date: str | None = Query(None, description="Np. 2026-03-01"),
):
    parsed_windows = [int(x.strip()) for x in windows.split(",") if x.strip()]

    return calculate_moving_average(
        item_id=item_id,
        windows=parsed_windows,
        limit=limit,
        from_date=from_date,
        to_date=to_date,
    )