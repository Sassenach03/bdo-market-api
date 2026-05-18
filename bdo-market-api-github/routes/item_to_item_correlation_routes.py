from fastapi import APIRouter, Query
from services.item_to_item_correlation import calculate_item_to_item_correlation

router = APIRouter()


@router.get("/api/items/correlation-between-items")
def get_item_to_item_correlation(
    item_a_id: int = Query(..., description="ID pierwszego itemu"),
    item_b_id: int = Query(..., description="ID drugiego itemu"),
    metric: str = Query(default="base_price", description="Np. base_price"),
    max_lag: int = Query(default=10, ge=0, le=150),
    limit: int | None = Query(default=200, ge=10, le=5000),
    from_date: str | None = Query(default=None),
    to_date: str | None = Query(default=None),
):
    return calculate_item_to_item_correlation(
        item_a_id=item_a_id,
        item_b_id=item_b_id,
        metric=metric,
        max_lag=max_lag,
        limit=limit,
        from_date=from_date,
        to_date=to_date,
    )