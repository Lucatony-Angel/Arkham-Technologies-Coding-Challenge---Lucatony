import pandas as pd
from backend.app.services.ingestion import clean_rows, build_dim_date

def test_valid_row_passes_through():
    rows = [{"period": "2025-06-15", "capacity": "100000", "outage": "3000", "percentOutage": "3.0"}]
    result = clean_rows(rows)
    assert len(result) == 1
    assert result[0]["capacity_mw"] == 100000.0
    assert result[0]["outage_mw"] == 3000.0
    assert result[0]["percent_outage"] == 3.0


def test_missing_field_is_skipped():
    rows = [{"period": "2025-06-15", "capacity": "100000", "outage": "3000"}]
    result = clean_rows(rows)
    assert len(result) == 0


def test_bad_float_is_skipped():
    rows = [{"period": "2025-06-15", "capacity": "N/A", "outage": "3000", "percentOutage": "3.0"}]
    result = clean_rows(rows)
    assert len(result) == 0

def test_mixed_batch():
    rows = [
        {"period": "2025-06-15", "capacity": "100000", "outage": "3000", "percentOutage": "3.0"},
        {"period": "2025-06-16", "capacity": "100000", "outage": "3000"},
        {"period": "2025-06-15", "capacity": "N/A", "outage": "3000", "percentOutage": "3.0"},
    ]

    result = clean_rows(rows)
    assert len(result) == 1


def test_correct_year_month_quarter():
    fact_df = pd.DataFrame([{"period": "2025-06-15", "capacity_mw": 100000.0, "outage_mw": 3000.0, "percent_outage": 3.0}])
    result = build_dim_date(fact_df)
    assert result.iloc[0]["year"] == 2025
    assert result.iloc[0]["month"] == 6
    assert result.iloc[0]["quarter"] == 2

def test_correct_day_of_week():
     #2025-06-15 is a Sunday -> day_of_week = 6
     fact_df = pd.DataFrame([{"period": "2025-06-15", "capacity_mw": 100000.0, "outage_mw": 3000.0,"percent_outage": 3.0}])
     result = build_dim_date(fact_df)
     assert result.iloc[0]["day_of_week"] == 6

def test_row_count_matches():
    fact_df = pd.DataFrame([
        {"period": "2025-06-15", "capacity_mw": 100000.0, "outage_mw": 3000.0, "percent_outage": 3.0},
        {"period": "2025-06-15", "capacity_mw": 100000.0, "outage_mw": 3000.0, "percent_outage": 3.0},
    ])
    result = build_dim_date(fact_df)
    assert len(result) == len(fact_df)