from repository.item_history_repository import load_item_history
from services.market_features_service import calculate_market_features
from services.market_classifier_service import classify_market
from services.strategy_selector import select_algorithms


def analyze_market(item_id: int, limit: int | None = 200) -> dict:
    df = load_item_history(item_id=item_id)

    if df.empty:
        return {"error": "brak danych"}

    if limit is not None and limit > 0:
        df = df.tail(limit).reset_index(drop=True)

    features = calculate_market_features(df)

    if "error" in features:
        return {
            "item_id": item_id,
            "error": features["error"],
        }


    classification = classify_market(features)

    if classification is None:
        return {
            "item_id": item_id,
            "error": "classification returned None"
        }
    strategies = select_algorithms(classification["type"])


    return {
        "item_id": item_id,
        "count": len(df),
        "market_type": classification["type"],
        "trend_strength_label": classification["trend_strength_label"],
        "trend_quality_label": classification["trend_quality_label"],
        "recommended_algorithms": strategies,
        "features": features,
    }
