import pandas as pd

from repository.item_history_repository import load_item_history
from utils.analysis_helpers import add_basic_indicators, safe_round
from services.support_resistance_service import detect_support_resistance


def add_bollinger_bands(
    df: pd.DataFrame,
    window: int = 20,
    num_std: float = 2.0
) -> pd.DataFrame:
    df = df.copy()

    middle = df["base_price"].rolling(window=window).mean()
    std = df["base_price"].rolling(window=window).std(ddof=0)

    df["bb_middle"] = middle
    df["bb_upper"] = middle + num_std * std
    df["bb_lower"] = middle - num_std * std

    df["bb_position"] = (df["base_price"] - df["bb_lower"]) / (
        (df["bb_upper"] - df["bb_lower"]) + 1e-9
    )

    return df


def is_near_level(
    price: float,
    level: float | None,
    threshold: float = 0.03
) -> bool:
    if level is None or level == 0:
        return False
    return abs(price - level) / level <= threshold


def generate_signal(
    row: pd.Series,
    support: float | None,
    resistance: float | None
) -> str:
    price = row["base_price"]
    rsi = row["rsi_14"]
    macd = row["macd"]
    macd_signal = row["macd_signal"]
    bb_position = row["bb_position"]

    near_support = is_near_level(price, support, threshold=0.03)
    near_resistance = is_near_level(price, resistance, threshold=0.03)

    if (
        rsi < 40
        and near_support
        and macd >= macd_signal
        and bb_position <= 0.35
    ):
        return "buy"

    if (
        rsi > 60
        and near_resistance
        and macd < macd_signal
        and bb_position >= 0.65
    ):
        return "sell"

    return "hold"


def evaluate_signal(
    signal: str,
    current_price: float,
    future_price: float
) -> dict:
    market_return_pct = (future_price - current_price) / current_price
    price_change = future_price - current_price


    if future_price == current_price:
        return {
            "price_change": float(price_change),
            "market_return_pct": float(market_return_pct),
            "strategy_return_pct": 0.0,
            "is_correct": None,
            "outcome": "neutral",
        }

    if signal == "buy":
        strategy_return_pct = market_return_pct
        is_correct = future_price > current_price
        outcome = "win" if is_correct else "loss"

    elif signal == "sell":
        strategy_return_pct = (current_price - future_price) / current_price
        is_correct = future_price < current_price
        outcome = "win" if is_correct else "loss"

    else:
        strategy_return_pct = 0.0
        is_correct = None
        outcome = "neutral"

    return {
        "price_change": float(price_change),
        "market_return_pct": float(market_return_pct),
        "strategy_return_pct": float(strategy_return_pct),
        "is_correct": is_correct,
        "outcome": outcome,
    }


def run_backtest(
    item_id: int,
    horizon_steps: int = 24,
    limit: int | None = 500,
    from_date: str | None = None,
    to_date: str | None = None,
    min_history: int = 120,
) -> dict:
    df = load_item_history(
        item_id=item_id,
        from_date=from_date,
        to_date=to_date
    )

    if df.empty:
        return {
            "item_id": item_id,
            "count": 0,
            "signals": [],
            "summary": None,
            "reason": "brak danych",
        }

    df = add_basic_indicators(df)
    df = add_bollinger_bands(df)

    if limit is not None and limit > 0:
        df = df.tail(limit).reset_index(drop=True)

    signals = []


    for i in range(min_history, len(df) - horizon_steps):
        history_df = df.iloc[:i + 1].copy()
        row = history_df.iloc[-1]


        if (
            pd.isna(row["rsi_14"])
            or pd.isna(row["macd"])
            or pd.isna(row["macd_signal"])
            or pd.isna(row["bb_position"])
        ):
            continue


        support, resistance, _, _ = detect_support_resistance(
            history_df,
            bins_count=12,
            recent_days=90
        )

        signal = generate_signal(row, support, resistance)

        if signal == "hold":
            continue

        current_price = float(row["base_price"])
        future_price = float(df.iloc[i + horizon_steps]["base_price"])

        evaluation = evaluate_signal(
            signal=signal,
            current_price=current_price,
            future_price=future_price
        )

        signals.append({
            "recorded_at": row["recorded_at"].isoformat(),
            "signal": signal,
            "current_price": safe_round(current_price, 2),
            "future_price": safe_round(future_price, 2),
            "price_change": safe_round(evaluation["price_change"], 2),
            "market_return_pct": safe_round(evaluation["market_return_pct"], 4),
            "strategy_return_pct": safe_round(evaluation["strategy_return_pct"], 4),
            "is_correct": evaluation["is_correct"],
            "outcome": evaluation["outcome"],
            "rsi_14": safe_round(row["rsi_14"], 2),
            "macd": safe_round(row["macd"], 4),
            "macd_signal": safe_round(row["macd_signal"], 4),
            "bb_position": safe_round(row["bb_position"], 4),
            "support": safe_round(support, 2),
            "resistance": safe_round(resistance, 2),
            "near_support": is_near_level(current_price, support),
            "near_resistance": is_near_level(current_price, resistance),
        })

    if not signals:
        return {
            "item_id": item_id,
            "count": len(df),
            "filters": {
                "horizon_steps": horizon_steps,
                "limit": limit,
                "from_date": from_date,
                "to_date": to_date,
                "min_history": min_history,
            },
            "signals": [],
            "summary": {
                "total_signals": 0,
                "buy_signals": 0,
                "sell_signals": 0,
                "win_rate": None,
                "avg_strategy_return_pct": None,
                "avg_market_return_pct": None,
                "neutral_signals": 0,
            },
        }

    total_signals = len(signals)
    buy_signals = sum(1 for s in signals if s["signal"] == "buy")
    sell_signals = sum(1 for s in signals if s["signal"] == "sell")
    neutral_signals = sum(1 for s in signals if s["outcome"] == "neutral")

    decided_signals = [s for s in signals if s["is_correct"] is not None]
    wins = sum(1 for s in decided_signals if s["is_correct"] is True)
    losses = sum(1 for s in decided_signals if s["is_correct"] is False)

    win_rate = None
    if decided_signals:
        win_rate = wins / len(decided_signals)

    avg_strategy_return_pct = sum(s["strategy_return_pct"] for s in signals) / total_signals
    avg_market_return_pct = sum(s["market_return_pct"] for s in signals) / total_signals

    buy_returns = [s["strategy_return_pct"] for s in signals if s["signal"] == "buy"]
    sell_returns = [s["strategy_return_pct"] for s in signals if s["signal"] == "sell"]

    avg_buy_return_pct = sum(buy_returns) / len(buy_returns) if buy_returns else None
    avg_sell_return_pct = sum(sell_returns) / len(sell_returns) if sell_returns else None

    return {
        "item_id": item_id,
        "count": len(df),
        "filters": {
            "horizon_steps": horizon_steps,
            "limit": limit,
            "from_date": from_date,
            "to_date": to_date,
            "min_history": min_history,
        },
        "signals": signals,
        "summary": {
            "total_signals": total_signals,
            "buy_signals": buy_signals,
            "sell_signals": sell_signals,
            "neutral_signals": neutral_signals,
            "wins": wins,
            "losses": losses,
            "win_rate": safe_round(win_rate, 4),
            "avg_strategy_return_pct": safe_round(avg_strategy_return_pct, 4),
            "avg_market_return_pct": safe_round(avg_market_return_pct, 4),
            "avg_buy_return_pct": safe_round(avg_buy_return_pct, 4),
            "avg_sell_return_pct": safe_round(avg_sell_return_pct, 4),
        },
    }