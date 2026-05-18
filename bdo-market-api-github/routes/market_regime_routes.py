from fastapi import APIRouter, Query
from services.market_regime_service import calculate_market_regime

router = APIRouter()


@router.get("/api/items/{item_id}/market-regime")
def get_market_regime(
    item_id: int,
    from_date: str | None = Query(default=None),
    to_date: str | None = Query(default=None),
):
    return calculate_market_regime(
        item_id=item_id,
        from_date=from_date,
        to_date=to_date,
    )