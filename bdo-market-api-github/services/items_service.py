from db import get_connection


def get_all_items(limit: int = 15000):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT item_id, name
        FROM items
        ORDER BY item_id
        LIMIT %s
    """, (limit,))

    rows = cur.fetchall()

    cur.close()
    conn.close()

    return [
        {
            "item_id": row[0],
            "name": row[1]
        }
        for row in rows
    ]