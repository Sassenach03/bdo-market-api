from fastapi import APIRouter
from services.market_analysis_service import analyze_market

router = APIRouter()


@router.get("/api/items/{item_id}/market-analysis")
def get_market_analysis(item_id: int):
    return analyze_market(item_id)