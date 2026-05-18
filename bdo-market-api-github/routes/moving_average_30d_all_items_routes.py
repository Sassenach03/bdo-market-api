from fastapi import APIRouter, Query
from services.moving_average_30d_all_items_service import calculate_moving_average_for_all_items

router = APIRouter()


@router.get("/api/items/moving-averages/all")
def get_all_moving_averages(
    windows: str = Query(default="7,30", description="Np. 7,30"),
    days: int = Query(default=30, description="Ile dni wstecz"),
    limit_per_item: int | None = Query(default=None, description="Ile ostatnich rekordów na item"),
):
    parsed_windows = [int(x.strip()) for x in windows.split(",") if x.strip()]

    return calculate_moving_average_for_all_items(
        windows=parsed_windows,
        days=days,
        limit_per_item=limit_per_item,
    )