"""Load, clean, and validate order data."""
import pandas as pd

REQUIRED_COLUMNS = ["order_id", "customer_id", "order_date", "product", "quantity", "price"]
OUTPUT_COLUMNS = REQUIRED_COLUMNS + ["total"]


def load_csv(path) -> pd.DataFrame:
    """Read the CSV as text so pandas doesn't silently convert (or hide) bad values."""
    df = pd.read_csv(path, dtype=str)
    missing = set(REQUIRED_COLUMNS) - set(df.columns)
    if missing:
        raise ValueError(f"CSV is missing required columns: {sorted(missing)}")
    return df[REQUIRED_COLUMNS]


def standardize_text(df: pd.DataFrame) -> pd.DataFrame:
    """Trim whitespace, fix casing, and turn empty strings into proper missing values."""
    df = df.copy()
    for col in ["order_id", "customer_id", "product"]:
        df[col] = df[col].str.strip()
    df["product"] = df["product"].str.title()
    df["customer_id"] = df["customer_id"].str.upper()
    return df.replace({"": pd.NA})


def validate(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Split rows into (clean, rejected). Rejected rows get a reject_reason column."""
    df = df.copy()
    checks = {}  # message -> boolean mask of rows that FAIL that check

    # 1. Missing values (checked before type conversion)
    for col in REQUIRED_COLUMNS:
        checks[f"missing {col}"] = df[col].isna()

    # 2. Convert types. Anything unconvertible becomes NaN/NaT instead of crashing.
    df["order_date"] = pd.to_datetime(df["order_date"], format="mixed", errors="coerce")
    df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce")
    df["price"] = pd.to_numeric(df["price"], errors="coerce")

    # 3. Values that existed but couldn't be converted = invalid (not just missing)
    for col in ["order_date", "quantity", "price"]:
        checks[f"invalid {col}"] = df[col].isna() & ~checks[f"missing {col}"]

    # 4. Business rules
    checks["quantity must be > 0"] = df["quantity"] <= 0
    checks["quantity must be whole number"] = df["quantity"] % 1 != 0
    checks["price must be > 0"] = df["price"] <= 0
    checks["duplicate order_id"] = df.duplicated(subset="order_id", keep="first")

    # Build a combined reason string for each row
    reason = pd.Series("", index=df.index)
    for message, mask in checks.items():
        reason = reason.where(~mask, reason + message + "; ")

    is_bad = reason != ""
    rejected = df[is_bad].copy()
    rejected["reject_reason"] = reason[is_bad].str.rstrip("; ")

    clean = df[~is_bad].copy()
    clean["quantity"] = clean["quantity"].astype(int)
    clean["order_date"] = clean["order_date"].dt.strftime("%Y-%m-%d")  # standard format
    clean["total"] = (clean["quantity"] * clean["price"]).round(2)
    return clean[OUTPUT_COLUMNS], rejected


def clean_data(raw: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    """Full pipeline: standardize -> remove exact duplicates -> validate."""
    rows_loaded = len(raw)
    df = standardize_text(raw)

    before = len(df)
    df = df.drop_duplicates()
    duplicates_removed = before - len(df)

    clean, rejected = validate(df)
    stats = {
        "rows_loaded": rows_loaded,
        "duplicates_removed": duplicates_removed,
        "rows_rejected": len(rejected),
        "rows_clean": len(clean),
    }
    return clean, rejected, stats