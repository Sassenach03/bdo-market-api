from fastapi import APIRouter
from services.items_service import get_all_items

router = APIRouter()


@router.get("/api/items")
def read_all_items():
    return get_all_items()