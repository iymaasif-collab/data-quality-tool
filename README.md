# Data Quality & Management Tool

A Python + SQL application that imports messy CSV order data, validates and cleans it with Pandas, stores the valid records in SQLite, and generates sales reports.

## What it does

1. **Imports** raw order data from a CSV file
2. **Cleans** it: trims whitespace, standardizes text casing, converts mixed date formats to `YYYY-MM-DD`, removes duplicates
3. **Validates** every row (missing values, invalid types, business rules) and sends failures to a separate rejected file with the reason
4. **Stores** clean records in a SQLite database with constraints
5. **Queries** the database with SQL for business metrics
6. **Reports** results as CSV files and a chart

## Tech stack

Python, Pandas, SQLite, Matplotlib, Pytest

## Project structure

```
data-quality-tool/
├── data/
│   └── orders.csv
├── src/
│   ├── main.py
│   ├── data_cleaner.py
│   ├── database.py
│   ├── reports.py
│   └── generate_sample_data.py
├── output/
│   ├── sales_report.png
│   ├── data_quality_summary.csv
│   ├── rejected_records.csv
│   └── monthly_sales.csv
├── tests/
│   └── test_cleaner.py
├── requirements.txt
└── README.md
```

## How to run

```bash
git clone https://github.com/iymaasif-collab/data-quality-tool.git
cd data-quality-tool
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

python src/generate_sample_data.py   # creates a messy sample dataset
python src/main.py                   # runs the full pipeline
python -m pytest -v                  # runs the tests
```

## Validation rules

| Check | Description |
|---|---|
| Missing values | Any required field left blank |
| Invalid date | Value that can't be parsed as a date |
| Invalid quantity or price | Non-numeric values |
| Quantity must be > 0 | Rejects zero and negative quantities |
| Quantity must be a whole number | Rejects values like 2.5 |
| Price must be > 0 | Rejects zero and negative prices |
| Duplicate order ID | Only the first occurrence is kept |

Rejected rows are not silently dropped. They are written to `output/rejected_records.csv` with a `reject_reason` column.

The SQLite table also enforces a `PRIMARY KEY` and `CHECK` constraints, so the database rejects bad data even if the Python validation has a bug.

## Sample output

```
=== Business Metrics ===
Total sales:          174885.0
Average order value:  1005.09

Top products:
  product  units_sold  revenue
  Laptop         100 120000.0
 Monitor          78  23400.0
 Headset          97  14550.0
  Webcam         102   9180.0
Keyboard          66   5280.0

Orders by month:
   month  orders  revenue
2025-01      12  10160.0
2025-02      14   5125.0
2025-03      11   8395.0
2025-04      15   5985.0
2025-05      17  19535.0
2025-06      21  30080.0
2025-07      15  23390.0
2025-08      14  20160.0
2025-09      10  13405.0
2025-10      17  16025.0
2025-11      14  12465.0
2025-12      14  10160.0
<img width="2798" height="1052" alt="24660664-D434-4F04-A399-9CA485BDD27E" src="https://github.com/user-attachments/assets/03c2a064-f5e6-473c-96a6-0784d7b52020" />
