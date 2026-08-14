"""
load_to_db.py
Loads clean_orders.csv into a SQLite database using an UPSERT pattern
(insert new rows, update existing ones) rather than a naive full reload.

This simulates a real incremental load: running this script multiple
times on updated data will not create duplicates, and will correctly
update rows whose values have changed.
"""
import sqlite3
import pandas as pd

DB_PATH = 'orders.db'
CLEAN_CSV = 'output/clean_orders.csv'

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS orders (
    order_id INTEGER PRIMARY KEY,
    customer_name TEXT,
    email TEXT,
    order_date TEXT,
    amount REAL,
    status TEXT,
    region TEXT,
    loaded_at TEXT DEFAULT CURRENT_TIMESTAMP
);
"""

# SQLite's upsert syntax: ON CONFLICT ... DO UPDATE
# (Postgres uses near-identical syntax; SQL Server/MySQL use MERGE / ON DUPLICATE KEY instead)
UPSERT_SQL = """
INSERT INTO orders (order_id, customer_name, email, order_date, amount, status, region)
VALUES (?, ?, ?, ?, ?, ?, ?)
ON CONFLICT(order_id) DO UPDATE SET
    customer_name = excluded.customer_name,
    email = excluded.email,
    order_date = excluded.order_date,
    amount = excluded.amount,
    status = excluded.status,
    region = excluded.region;
"""


def load():
    df = pd.read_csv(CLEAN_CSV)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(CREATE_TABLE_SQL)

    before_count = cur.execute("SELECT COUNT(*) FROM orders").fetchone()[0]

    rows = df[['order_id', 'customer_name', 'email', 'order_date', 'amount', 'status', 'region']].values.tolist()
    cur.executemany(UPSERT_SQL, rows)
    conn.commit()

    after_count = cur.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
    print(f"[LOAD] Rows in orders table before: {before_count}")
    print(f"[LOAD] Rows in orders table after:  {after_count}")
    print(f"[LOAD] Upserted {len(rows)} rows from {CLEAN_CSV}")

    conn.close()


if __name__ == '__main__':
    load()
