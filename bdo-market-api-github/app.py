from fastapi import FastAPI
from routes.moving_average_routes import router as moving_average_router
from routes.momentum_routes import router as momentum_router
from routes.support_resistance_routes import router as support_resistance_router
from routes.market_regime_routes import router as market_regime_router
from routes.forecast_routes import router as forecast_router
from routes.summary_routes import router as summary_router
from routes.rsi_support_resistance_routes import router as rsi_support_resistance_router
from routes.macd_routes import router as macd_router
from routes.correlation_routes import router as correlation_router
from routes.item_to_item_correlation_routes import router as item_to_item_correlation_router
from routes.market_analysis_routes import router as market_analysis_router
from routes.bollinger_bands_routes import router as bollinger_bands_router
from routes.backtest_routes import router as backtest_router
from routes.item_dashboard_routes import router as item_dashboard_router
from routes.items_router import router as items_router
from routes.moving_average_30d_all_items_routes import router as moving_average_30d_all_items_router

app = FastAPI(title="BDO Market Analyzer API")

app.include_router(moving_average_router)
app.include_router(momentum_router)
app.include_router(support_resistance_router)
app.include_router(market_regime_router)
app.include_router(forecast_router)
app.include_router(summary_router)
app.include_router(rsi_support_resistance_router)
app.include_router(macd_router)
app.include_router(correlation_router)
app.include_router(item_to_item_correlation_router)
app.include_router(market_analysis_router)
app.include_router(bollinger_bands_router)
app.include_router(backtest_router)
app.include_router(item_dashboard_router)
app.include_router(items_router)
app.include_router(moving_average_30d_all_items_router)