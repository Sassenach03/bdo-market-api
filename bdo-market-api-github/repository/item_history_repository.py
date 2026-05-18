import pandas as pd
from db import get_connection


def load_item_history(
    item_id: int,
    from_date: str | None = None,
    to_date: str | None = None,
) -> pd.DataFrame:
    query = """
    SELECT
        recorded_at,
        base_price,
        current_stock,
        trade_volume
    FROM bdolytics_history
    WHERE item_id = %s
    """

    params = [item_id]

    if from_date:
        query += " AND recorded_at >= %s"
        params.append(from_date)

    if to_date:
        query += " AND recorded_at < (%s::timestamp + interval '1 day')"
        params.append(to_date)

    query += " ORDER BY recorded_at ASC"

    conn = get_connection()
    try:
        df = pd.read_sql_query(query, conn, params=params)
    finally:
        conn.close()

    if df.empty:
        return df

    df["recorded_at"] = pd.to_datetime(df["recorded_at"])
    df = df.sort_values("recorded_at").reset_index(drop=True)
    return df