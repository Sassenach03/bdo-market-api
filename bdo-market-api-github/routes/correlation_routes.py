from fastapi import APIRouter, Query
from services.correlation_service import calculate_series_correlation

router = APIRouter()


@router.get("/api/items/{item_id}/correlation")
def get_correlation(
    item_id: int,
    series_a: str = Query(..., description="Np. base_price"),
    series_b: str = Query(..., description="Np. trade_volume"),
    max_lag: int = Query(default=10, ge=0, le=50),
    limit: int | None = Query(default=200, ge=10, le=5000),
    from_date: str | None = Query(default=None),
    to_date: str | None = Query(default=None),
):
    return calculate_series_correlation(
        item_id=item_id,
        series_a_name=series_a,
        series_b_name=series_b,
        max_lag=max_lag,
        limit=limit,
        from_date=from_date,
        to_date=to_date,
    )