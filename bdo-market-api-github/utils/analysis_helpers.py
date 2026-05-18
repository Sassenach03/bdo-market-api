import numpy as np
import pandas as pd


def add_basic_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df["price_change"] = df["base_price"].diff()
    df["stock_change"] = df["current_stock"].diff()
    df["volume_change"] = df["trade_volume"].diff()

    macd_df = calculate_macd(df["base_price"])
    df["macd"] = macd_df["macd"]
    df["macd_signal"] = macd_df["signal"]
    df["macd_histogram"] = macd_df["histogram"]

    df["rsi_14"] = calculate_rsi(df["base_price"], 14)

    df["ma7"] = df["base_price"].rolling(7).mean()
    df["ma30"] = df["base_price"].rolling(30).mean()

    df["return_1d"] = df["base_price"].pct_change(1)
    df["return_7d"] = df["base_price"].pct_change(7)
    df["return_30d"] = df["base_price"].pct_change(30)
    df["return_90d"] = df["base_price"].pct_change(90)

    df["ma7_slope"] = df["ma7"].diff(3)
    df["ma30_slope"] = df["ma30"].diff(3)

    df["volatility_7"] = df["base_price"].pct_change().rolling(7).std()
    df["volatility_30"] = df["base_price"].pct_change().rolling(30).std()

    df["price_vs_ma30"] = (df["base_price"] - df["ma30"]) / df["ma30"]
    df["ma_gap"] = (df["ma7"] - df["ma30"]) / df["ma30"]

    df["volume_ma7"] = df["trade_volume"].rolling(7).mean()
    df["volume_spike"] = df["trade_volume"] / (df["volume_ma7"] + 1)

    rolling_min_30 = df["base_price"].rolling(30).min()
    rolling_max_30 = df["base_price"].rolling(30).max()
    rolling_min_90 = df["base_price"].rolling(90).min()
    rolling_max_90 = df["base_price"].rolling(90).max()

    df["price_position_30"] = (
        (df["base_price"] - rolling_min_30) /
        (rolling_max_30 - rolling_min_30 + 1e-9)
    )

    df["price_position_90"] = (
        (df["base_price"] - rolling_min_90) /
        (rolling_max_90 - rolling_min_90 + 1e-9)
    )

    df["liquidity_7d"] = df["trade_volume"].rolling(7).mean()
    df["liquidity_30d"] = df["trade_volume"].rolling(30).mean()
    df["liquidity_90d"] = df["trade_volume"].rolling(90).mean()

    df["liquidity_change"] = (
        (df["liquidity_7d"] - df["liquidity_30d"]) /
        (df["liquidity_30d"] + 1)
    )

    return df


def safe_round(value, digits=2):
    if pd.isna(value):
        return None
    return round(float(value), digits)

def calculate_rsi(series: pd.Series, periods: int = 14) -> pd.Series:
    delta = series.diff()
    gains = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gains.rolling(window=periods).mean()
    avg_loss = loss.rolling(window=periods).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100/(1 + rs))
    return rsi
def calculate_macd(
        series: pd.Series,
        fast_period: int = 12,
        slow_period: int = 26,
        signal_period: int = 9
) -> pd.DataFrame:
    ema_fast = series.ewm(span=fast_period, adjust=False).mean()
    ema_slow = series.ewm(span=slow_period, adjust=False).mean()

    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal_period, adjust=False).mean()
    histogram = macd_line - signal_line
    return pd.DataFrame({
        "macd": macd_line,
        "signal": signal_line,
        "histogram": histogram
    })
def min_max_normalize(series: pd.Series) -> pd.Series:
    min_value = series.min()
    max_value = series.max()

    if pd.isna(min_value) or pd.isna(max_value):
        return pd.Series([None] * len(series), index=series.index)
    if max_value == min_value:
        return pd.Series([0.5] * len(series), index=series.index)
    return (series - min_value) / (max_value - min_value)
def calculate_lagged_correlation(
        series_a: pd.Series,
        series_b: pd.Series,
        lag: int = 0,
) -> float | None:
    df = pd.DataFrame({
        "series_a": series_a,
        "series_b": series_b,
    }).copy()

    if lag > 0:
        df["series_b"] = df["series_b"].shift(-lag)
    elif lag < 0:
        df["series_b"] = df["series_b"].shift(abs(lag))
    df = df.dropna()

    if len(df) < 2:
        return None
    correlation = df["series_a"].corr(df["series_b"])

    if pd.isna(correlation):
        return None

    return float(correlation)
def calculate_lag_range_correlations(
    series_a: pd.Series,
    series_b: pd.Series,
    max_lag: int,
) -> list[dict]:
    results = []

    for lag in range(0, max_lag + 1):
        correlation = calculate_lagged_correlation(
            series_a=series_a,
            series_b=series_b,
            lag=lag,
        )

        results.append({
            "lag": lag,
            "correlation": None if correlation is None else round(correlation, 4),
        })

    return results
def find_best_lag(lag_results: list[dict]) -> tuple[int | None, float | None]:
    valid_results = [
        item for item in lag_results
        if item["correlation"] is not None
    ]

    if not valid_results:
        return None, None

    best_item = max(valid_results, key=lambda x: abs(x["correlation"]))
    return best_item["lag"], best_item["correlation"]