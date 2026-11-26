import pandas as pd
from data_cleaner import clean_data

VALID = {
    "order_id": "ORD-1", "customer_id": "cust-1", "order_date": "2025-01-15",
    "product": " laptop ", "quantity": "2", "price": "100.0",
}


def make_df(*overrides):
    return pd.DataFrame([{**VALID, **o} for o in overrides])


def test_valid_row_is_cleaned_and_standardized():
    clean, rejected, _ = clean_data(make_df({}))
    assert len(rejected) == 0
    row = clean.iloc[0]
    assert row["product"] == "Laptop"
    assert row["customer_id"] == "CUST-1"
    assert row["total"] == 200.0


def test_exact_duplicates_are_removed():
    clean, _, stats = clean_data(make_df({}, {}))
    assert len(clean) == 1
    assert stats["duplicates_removed"] == 1


def test_negative_quantity_is_rejected():
    clean, rejected, _ = clean_data(make_df({"quantity": "-3"}))
    assert len(clean) == 0
    assert "quantity must be > 0" in rejected.iloc[0]["reject_reason"]


def test_missing_customer_is_rejected():
    _, rejected, _ = clean_data(make_df({"customer_id": ""}))
    assert "missing customer_id" in rejected.iloc[0]["reject_reason"]


def test_invalid_price_is_rejected():
    _, rejected, _ = clean_data(make_df({"price": "abc"}))
    assert "invalid price" in rejected.iloc[0]["reject_reason"]


def test_bad_date_is_rejected():
    _, rejected, _ = clean_data(make_df({"order_date": "not a date"}))
    assert "invalid order_date" in rejected.iloc[0]["reject_reason"]


def test_mixed_date_formats_are_standardized():
    clean, _, _ = clean_data(make_df(
        {"order_id": "A", "order_date": "01/15/2025"},
        {"order_id": "B", "order_date": "15-Jan-2025"},
    ))
    assert set(clean["order_date"]) == {"2025-01-15"}