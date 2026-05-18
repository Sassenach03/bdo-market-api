from fastapi import APIRouter, Query
from services.backtest_service import run_backtest

router = APIRouter()


@router.get("/api/items/{item_id}/backtest")
def get_backtest(
    item_id: int,
    horizon_steps: int = Query(default=24, ge=1, le=500),
    limit: int | None = Query(default=500, ge=50, le=5000),
    from_date: str | None = Query(default=None),
    to_date: str | None = Query(default=None),
):
    return run_backtest(
        item_id=item_id,
        horizon_steps=horizon_steps,
        limit=limit,
        from_date=from_date,
        to_date=to_date,
    )