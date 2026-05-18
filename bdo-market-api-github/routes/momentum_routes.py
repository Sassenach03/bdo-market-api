from fastapi import APIRouter, Query
from services.momentum_service import calculate_momentum

router = APIRouter()


@router.get("/api/items/{item_id}/momentum")
def get_momentum(
    item_id: int,
    from_date: str | None = Query(default=None, description="Np. 2026-01-01"),
    to_date: str | None = Query(default=None, description="Np. 2026-03-01"),
):
    return calculate_momentum(
        item_id=item_id,
        from_date=from_date,
        to_date=to_date,
    )