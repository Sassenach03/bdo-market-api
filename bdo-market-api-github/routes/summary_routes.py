from fastapi import APIRouter, Query
from services.summary_service import calculate_summary

router = APIRouter()


@router.get("/api/items/{item_id}/summary")
def get_summary(
    item_id: int,
    from_date: str | None = Query(default=None),
    to_date: str | None = Query(default=None),
):
    return calculate_summary(
        item_id=item_id,
        from_date=from_date,
        to_date=to_date,
    )