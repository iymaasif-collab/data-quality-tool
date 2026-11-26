"""Run the full pipeline: import -> clean -> store -> query -> report."""
from pathlib import Path

from data_cleaner import clean_data, load_csv
from database import QUERIES, create_table, get_connection, insert_orders, run_query
from reports import save_chart, save_quality_summary, save_rejected

ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "data" / "orders.csv"
DB_FILE = ROOT / "output" / "orders.db"
OUTPUT = ROOT / "output"


def main() -> None:
    # 1. Import
    raw = load_csv(DATA_FILE)

    # 2. Clean and validate
    clean, rejected, stats = clean_data(raw)
    print("=== Data Quality Summary ===")
    for key, value in stats.items():
        print(f"{key:>20}: {value}")

    # 3. Store in SQLite
    conn = get_connection(DB_FILE)
    create_table(conn)
    insert_orders(conn, clean)

    # 4. Query
    results = {name: run_query(conn, sql) for name, sql in QUERIES.items()}
    conn.close()

    print("\n=== Business Metrics ===")
    print("Total sales:         ", results["total_sales"].iloc[0, 0])
    print("Average order value: ", results["average_order_value"].iloc[0, 0])
    print("\nTop products:\n", results["top_products"].to_string(index=False))
    print("\nOrders by month:\n", results["orders_by_month"].to_string(index=False))

    # 5. Reports
    save_quality_summary(stats, OUTPUT / "data_quality_summary.csv")
    save_rejected(rejected, OUTPUT / "rejected_records.csv")
    results["orders_by_month"].to_csv(OUTPUT / "monthly_sales.csv", index=False)
    save_chart(results["orders_by_month"], results["top_products"], OUTPUT / "sales_report.png")
    print(f"\nReports saved to {OUTPUT}")


if __name__ == "__main__":
    main()