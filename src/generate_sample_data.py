"""Generate a messy orders.csv for testing the data quality tool."""
import csv
import random
from datetime import date, timedelta
from pathlib import Path

random.seed(42)  # makes the "random" data identical every run

PRODUCTS = {
    "Laptop": 1200.00, "Monitor": 300.00, "Keyboard": 80.00,
    "Mouse": 25.00, "Headset": 150.00, "Webcam": 90.00,
}
COLUMNS = ["order_id", "customer_id", "order_date", "product", "quantity", "price"]


def random_date() -> str:
    d = date(2025, 1, 1) + timedelta(days=random.randint(0, 364))
    # Deliberately mix date formats, like real data from different systems
    fmt = random.choice(["%Y-%m-%d", "%m/%d/%Y", "%d-%b-%Y"])
    return d.strftime(fmt)


def build_rows(n: int = 200) -> list[dict]:
    rows = []
    for i in range(1, n + 1):
        product = random.choice(list(PRODUCTS))
        rows.append({
            "order_id": f"ORD-{i:04d}",
            "customer_id": f"CUST-{random.randint(1, 40):03d}",
            "order_date": random_date(),
            "product": product,
            "quantity": random.randint(1, 5),
            "price": PRODUCTS[product],
        })
    return rows


def inject_errors(rows: list[dict]) -> list[dict]:
    bad = random.sample(range(len(rows)), 30)
    for i in bad[:6]:
        rows[i]["customer_id"] = ""                       # missing customer
    for i in bad[6:12]:
        rows[i]["quantity"] = random.choice([-2, -1, 0])  # invalid quantity
    for i in bad[12:17]:
        rows[i]["price"] = random.choice([-50, 0])        # invalid price
    for i in bad[17:22]:
        rows[i]["order_date"] = "not a date"              # unparseable date
    for i in bad[22:26]:
        rows[i]["product"] = f"  {rows[i]['product'].lower()} "  # messy text
    for i in bad[26:30]:
        rows[i]["quantity"] = ""                          # missing quantity

    rows.extend(random.sample(rows, 10))                  # 10 duplicate rows
    random.shuffle(rows)
    return rows


if __name__ == "__main__":
    rows = inject_errors(build_rows())
    path = Path(__file__).resolve().parent.parent / "data" / "orders.csv"
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} rows to {path}")