"""SQLite storage and SQL queries."""
import sqlite3
import pandas as pd

SCHEMA = """
CREATE TABLE orders (
    order_id    TEXT PRIMARY KEY,
    customer_id TEXT NOT NULL,
    order_date  TEXT NOT NULL,
    product     TEXT NOT NULL,
    quantity    INTEGER NOT NULL CHECK (quantity > 0),
    price       REAL NOT NULL CHECK (price > 0),
    total       REAL NOT NULL
);
"""

QUERIES = {
    "total_sales": """
        SELECT ROUND(SUM(total), 2) AS total_sales
        FROM orders;
    """,
    "average_order_value": """
        SELECT ROUND(AVG(total), 2) AS average_order_value
        FROM orders;
    """,
    "top_products": """
        SELECT product,
               SUM(quantity)       AS units_sold,
               ROUND(SUM(total), 2) AS revenue
        FROM orders
        GROUP BY product
        ORDER BY revenue DESC
        LIMIT 5;
    """,
    "orders_by_month": """
        SELECT strftime('%Y-%m', order_date) AS month,
               COUNT(*)                      AS orders,
               ROUND(SUM(total), 2)          AS revenue
        FROM orders
        GROUP BY month
        ORDER BY month;
    """,
}


def get_connection(db_path) -> sqlite3.Connection:
    return sqlite3.connect(db_path)


def create_table(conn: sqlite3.Connection) -> None:
    """Rebuild the table so the program can be re-run safely."""
    conn.execute("DROP TABLE IF EXISTS orders;")
    conn.execute(SCHEMA)
    conn.commit()


def insert_orders(conn: sqlite3.Connection, df: pd.DataFrame) -> None:
    df.to_sql("orders", conn, if_exists="append", index=False)
    conn.commit()


def run_query(conn: sqlite3.Connection, sql: str) -> pd.DataFrame:
    return pd.read_sql_query(sql, conn)