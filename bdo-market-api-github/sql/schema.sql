CREATE TABLE items (
    item_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL
);

CREATE TABLE bdolytics_history (
    id SERIAL PRIMARY KEY,
    item_id INTEGER NOT NULL,
    recorded_at TIMESTAMP NOT NULL,
    base_price NUMERIC,
    current_stock INTEGER,
    trade_volume INTEGER,
    CONSTRAINT fk_item
        FOREIGN KEY (item_id)
        REFERENCES items(item_id)
);

CREATE INDEX idx_bdolytics_history_item_id
ON bdolytics_history(item_id);

CREATE INDEX idx_bdolytics_history_item_recorded_at
ON bdolytics_history(item_id, recorded_at);