from fastapi import APIRouter, HTTPException, Query

from models.dashboard_models import DashboardResponse
from services.item_dashboard_service import build_item_dashboard

router = APIRouter(prefix="/items", tags=["Items Dashboard"])


@router.get("/{item_id}/dashboard", response_model=DashboardResponse)
def get_item_dashboard_route(
    item_id: int,
    chart_limit: int = Query(90, ge=30, le=365),
    forecast_days: int = Query(7, ge=1, le=30),
    history_days: int = Query(90, ge=30, le=365),
):
    try:
        return build_item_dashboard(
            item_id=item_id,
            chart_limit=chart_limit,
            forecast_days=forecast_days,
            history_days=history_days,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Dashboard error: {str(e)}")