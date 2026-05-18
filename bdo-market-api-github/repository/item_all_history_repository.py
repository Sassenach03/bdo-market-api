import pandas as pd
from db import get_connection

def load_all_items_history_last_days(days: int = 30) -> pd.DataFrame:
    query = """
            SELECT item_id, recorded_at, base_price
            FROM bdolytics_history
            WHERE recorded_at >= NOW() - (%s * INTERVAL '1 day')
            ORDER BY item_id, recorded_at \
            """
    conn = get_connection()
    try:
        df = pd.read_sql(query, conn, params=(days,))
        if not df.empty:
            df["recorded_at"] = pd.to_datetime(df["recorded_at"])
            df["base_price"] = pd.to_numeric(df["base_price"], errors="coerce")
        return df
    finally:
        conn.close()