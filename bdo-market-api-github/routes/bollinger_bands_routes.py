from fastapi import APIRouter, Query
from services.bollinger_bands_service import calculate_bolling_bands

router = APIRouter()


@router.get("/api/items/{item_id}/bollinger-bands")
def get_bollinger_bands(
    item_id: int,
    limit: int | None = Query(default=200, ge=1, le=5000),
    from_date: str | None = Query(default=None, description="Np. 2026-01-01"),
    to_date: str | None = Query(default=None, description="Np. 2026-03-01"),
):
    return calculate_bolling_bands(
        item_id=item_id,
        limit=limit,
        from_date=from_date,
        to_date=to_date,
    )