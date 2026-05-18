import numpy as np
import pandas as pd


def calculate_market_features(df: pd.DataFrame) -> dict:
    prices = df["base_price"].copy().dropna().reset_index(drop=True)

    if len(prices) < 30:
        return {"error": "za mało danych"}


    x = np.arange(len(prices))
    slope, intercept = np.polyfit(x, prices, 1)

    trend_line = slope * x + intercept


    ss_res = np.sum((prices - trend_line) ** 2)
    ss_tot = np.sum((prices - prices.mean()) ** 2)
    trend_r2 = 1 - (ss_res / (ss_tot + 1e-9))


    trend_strength = abs(slope) / (prices.mean() + 1e-9)


    returns = prices.pct_change()
    volatility = returns.std()


    net_change = abs(prices.iloc[-1] - prices.iloc[0])
    total_change = prices.diff().abs().sum()
    efficiency_ratio = net_change / (total_change + 1e-9)


    ma7 = prices.rolling(7).mean()
    ma30 = prices.rolling(30).mean()
    ma_cross_count = ((ma7 > ma30) != (ma7.shift(1) > ma30.shift(1))).sum()

    return {
        "trend_slope": float(slope),
        "trend_r2": float(trend_r2),
        "trend_strength": float(trend_strength),
        "volatility": float(volatility),
        "efficiency_ratio": float(efficiency_ratio),
        "ma_cross_count": int(ma_cross_count),
    }

