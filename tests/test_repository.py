import pandas as pd
from unittest.mock import patch
from backend.app.repository import get_outages

SAMPLE_DATA = pd.DataFrame([
    {"period": "2025-12-01", "capacity_mw": 100000.0, "outage_mw": 3000.0, "percent_outage": 3.0},
    {"period": "2025-12-02", "capacity_mw": 100000.0, "outage_mw": 4000.0, "percent_outage": 4.0},
    {"period": "2025-11-01", "capacity_mw": 100000.0, "outage_mw": 2000.0, "percent_outage": 2.0}
])

def mock_read_parquet(path):
    return SAMPLE_DATA

def test_limit():
    with patch("backend.app.repository.FACT_OUTAGES_PATH") as mock_path, \
         patch("pandas.read_parquet", mock_read_parquet):
        mock_path.exists.return_value = True
        result = get_outages(limit=2, offset=0)
        assert len(result) == 2

def test_offset():
    with patch("backend.app.repository.FACT_OUTAGES_PATH") as mock_path, \
         patch("pandas.read_parquet", mock_read_parquet):
        mock_path.exists.return_value = True
        result = get_outages(limit=10, offset=2)
        assert len(result) == 1


def test_date_from():
    with patch("backend.app.repository.FACT_OUTAGES_PATH") as mock_path, \
         patch("pandas.read_parquet", mock_read_parquet):
        mock_path.exists.return_value = True
        result = get_outages(date_from="2025-12-01")
        periods = []

        for r in result:
            periods.append(r["period"])

        for p in  periods:
            assert p >= "2025-12-01"

def test_date_to():
    with patch("backend.app.repository.FACT_OUTAGES_PATH") as mock_path, \
         patch("pandas.read_parquet", mock_read_parquet):
        mock_path.exists.return_value = True
        result = get_outages(date_to="2025-11-30")
        periods = []

        for r in result:
            periods.append(r["period"])

        for p in  periods:
            assert p <= "2025-11-30"

def test_missing_parquet_returns_empty():
    with patch("backend.app.repository.FACT_OUTAGES_PATH") as mock_path:
        mock_path.exists.return_value = False
        result = get_outages()
        assert result == []