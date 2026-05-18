from fastapi import APIRouter, Query
from services.support_resistance_service import calculate_support_resistance

router = APIRouter()


@router.get("/api/items/{item_id}/support-resistance")
def get_support_resistance(
    item_id: int,
    bins_count: int = Query(default=12, ge=4, le=50),
    recent_days: int = Query(default=90, ge=10, le=365),
    from_date: str | None = Query(default=None),
    to_date: str | None = Query(default=None),
):
    return calculate_support_resistance(
        item_id=item_id,
        from_date=from_date,
        to_date=to_date,
        bins_count=bins_count,
        recent_days=recent_days,
    )