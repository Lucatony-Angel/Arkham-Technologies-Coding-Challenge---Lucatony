from fastapi.testclient import TestClient
from unittest.mock import patch
from backend.app.main import app

client = TestClient(app)


# --- GET /data ---

def test_data_returns_200():
    with patch("backend.app.repository.FACT_OUTAGES_PATH") as mock_path, \
         patch("pandas.read_parquet") as mock_parquet:
        import pandas as pd
        mock_path.exists.return_value = True
        mock_parquet.return_value = pd.DataFrame([
            {"period": "2025-12-01", "capacity_mw": 100000.0, "outage_mw": 3000.0, "percent_outage": 3.0}
        ])
        response = client.get("/data")
        assert response.status_code == 200

def test_data_returns_correct_shape():
    with patch("backend.app.repository.FACT_OUTAGES_PATH") as mock_path, \
         patch("pandas.read_parquet") as mock_parquet:
        import pandas as pd
        mock_path.exists.return_value = True
        mock_parquet.return_value = pd.DataFrame([
            {"period": "2025-12-01", "capacity_mw": 100000.0, "outage_mw": 3000.0, "percent_outage": 3.0}
        ])
        response = client.get("/data")
        body = response.json()
        assert "data" in body
        assert "count" in body
        assert "offset" in body

def test_data_respects_limit():
    with patch("backend.app.repository.FACT_OUTAGES_PATH") as mock_path, \
         patch("pandas.read_parquet") as mock_parquet:
        import pandas as pd
        mock_path.exists.return_value = True
        mock_parquet.return_value = pd.DataFrame([
            {"period": "2025-12-01", "capacity_mw": 100000.0, "outage_mw": 3000.0, "percent_outage": 3.0},
            {"period": "2025-12-02", "capacity_mw": 100000.0, "outage_mw": 4000.0, "percent_outage": 4.0},
        ])
        response = client.get("/data?limit=1")
        assert len(response.json()["data"]) == 1

def test_data_empty_when_no_parquet():
    with patch("backend.app.repository.FACT_OUTAGES_PATH") as mock_path:
        mock_path.exists.return_value = False
        response = client.get("/data")
        assert response.status_code == 200
        assert response.json()["data"] == []


# --- POST /refresh ---

def test_refresh_returns_500_without_api_key():
    with patch("backend.app.core.config.settings.eia_api_key", None):
        response = client.post("/refresh")
        assert response.status_code == 500

def test_refresh_returns_result_on_success():
    mock_result = {
        "run_id": "abc-123",
        "row_count": 42,
        "fact_outages": "data/processed/fact_outages.parquet",
        "dim_date": "data/processed/dim_date.parquet",
        "ingestion_log": "data/processed/ingestion_log.parquet",
    }
    with patch("backend.app.api.routes.run_ingestion", return_value=mock_result):
        response = client.post("/refresh")
        assert response.status_code == 200
        assert response.json()["row_count"] == 42
