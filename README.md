# BDO Market Analytics API

FastAPI backend for analyzing market data from Black Desert Online.

The project reads historical item market data from a PostgreSQL database and provides analytical endpoints that can be used by a frontend dashboard or another client application.

The main goal of the project is to process historical item prices and calculate useful market indicators such as moving averages, momentum, volatility, RSI, MACD, Bollinger Bands, support and resistance levels, market regime and simple short-term forecasts.

## Project Status

This repository contains the core backend structure and selected analytical logic of the project.

The full production database dump is not included in this repository because of its size.  
Private configuration files such as `.env` are also not included.

The project is still under development and some modules may be refactored in the final version.

## Main Features

- REST API built with FastAPI
- PostgreSQL database integration
- Historical item price analysis
- Moving average calculation
- Momentum analysis
- Volatility calculation
- RSI indicator
- MACD indicator
- Bollinger Bands
- Support and resistance level detection
- Market regime classification
- Forecasting based on historical data
- Dashboard-oriented API responses

## Architecture

The project is divided into several layers:

```text
Client / Frontend
        ↓
FastAPI routes
        ↓
Services
        ↓
Repository
        ↓
PostgreSQL database
        ↓
pandas DataFrame
        ↓
JSON response
```

## Project Structure

```text
bdo-market-api/
│
├── app.py
├── db.py
├── requirements.txt
├── .gitignore
├── .env.example
│
├── models/
│   └── response models
│
├── repository/
│   └── database queries
│
├── routes/
│   └── API endpoints
│
├── services/
│   └── analytical logic
│
├── utils/
│   └── helper functions and indicators
│
└── sql/
    └── simplified database schema
```

## Layers Description

### Routes

The `routes/` directory contains FastAPI endpoints.

Routes are responsible for receiving HTTP requests, reading query parameters and passing them to the correct service.

Example responsibilities:

- get item history,
- return dashboard data,
- return market analysis results.

### Services

The `services/` directory contains the main business and analytical logic.

This layer calculates indicators and prepares data for API responses.

Example calculations:

- moving averages,
- momentum,
- volatility,
- RSI,
- MACD,
- Bollinger Bands,
- support and resistance levels,
- market regime,
- forecast values.

### Repository

The `repository/` directory is responsible for database access.

Repository functions execute SQL queries, load item history from PostgreSQL and return data as pandas DataFrames.

This keeps SQL logic separated from analytical calculations.

### Utils

The `utils/` directory contains helper functions used by different services.

This includes common indicator calculations, safe rounding, data preparation and reusable analytical functions.

### Models

The `models/` directory contains response models and data structures used by the API.

## Database

The backend uses PostgreSQL.

The main historical table stores item market data such as:

- item ID,
- recorded date,
- base price,
- current stock,
- trade volume.

A simplified schema is available in:

```text
sql/schema.sql
```

The full production database dump is not included in this repository.

## Environment Variables

Create a `.env` file based on `.env.example`.

Example:

```env
DB_HOST=localhost
DB_PORT=5432
POSTGRES_DB=bdo_market
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password_here
```

The real `.env` file should not be committed to GitHub.

## Running the API

Run the FastAPI application:

```bash
uvicorn app:app --reload
```

The API documentation will be available at:

```text
http://localhost:8000/docs
```

## Example API Flow

```text
GET /api/items/{item_id}/moving-averages
```

Example internal flow:

```text
Request
  ↓
FastAPI route
  ↓
Service function
  ↓
Repository function
  ↓
PostgreSQL query
  ↓
pandas DataFrame
  ↓
Calculated indicators
  ↓
JSON response
```

## Example Response

```json
{
  "item_id": 7905,
  "base_price": 120000,
  "ma7": 118500,
  "ma30": 115200,
  "trend": "uptrend"
}
```

## Technologies

- Python
- FastAPI
- PostgreSQL
- pandas
- NumPy
- statsmodels
- Uvicorn
- psycopg2

## Notes

This repository is intended to present the backend structure and analytical logic of the project.

The production version may include additional configuration, database dumps, scheduled data updates and deployment setup which are not included here.
