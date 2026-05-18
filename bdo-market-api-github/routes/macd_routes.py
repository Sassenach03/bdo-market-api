from fastapi import APIRouter, Query
from services.macd_service import calculate_macd_analysis

router = APIRouter()


@router.get("/api/items/{item_id}/macd")
def get_macd(
    item_id: int,
    limit: int | None = Query(default=200, ge=1, le=2000),
    from_date: str | None = Query(default=None, description="Np. 2026-01-01"),
    to_date: str | None = Query(default=None, description="Np. 2026-03-01"),
):
    return calculate_macd_analysis(
        item_id=item_id,
        limit=limit,
        from_date=from_date,
        to_date=to_date,
    )