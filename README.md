# Nuclear Outages Data Pipeline

A data pipeline that extracts US Nuclear Outages data from the EIA API, stores it in Parquet files, and exposes it via a REST API with a React frontend.

---

## Quick Start

### 1. Clone the repo

```bash
git clone <repo-url>
cd Arkham-Technologies-Coding-Challenge---Lucatony
```

### 2. Set up API key

Create a `.env` file in the project root:

```
EIA_API_KEY = your_api_key_here
```

Get a free API key at https://www.eia.gov/opendata/

### 3. Install backend dependencies

```bash
pip install -r backend/requirements.txt
```

### 4. Run the ingestion script

```bash
export EIA_API_KEY=your_api_key_here && python scripts/run_ingestion.py
```

### 5. Start the backend

```bash
uvicorn backend.app.main:app --reload
```

API will be available at `http://127.0.0.1:8000`

### 6. Start the frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend will be available at `http://localhost:5173`

---

## API Endpoints

### `GET /data`

Returns filtered and paginated nuclear outage records.

**Query parameters:**

| Parameter | Type | Default | Description |
|---|---|---|---|
| limit | int | 100 | Number of rows to return (max 1000) |
| offset | int | 0 | Number of rows to skip |
| date_from | string | — | Filter records on or after this date (YYYY-MM-DD) |
| date_to | string | — | Filter records on or before this date (YYYY-MM-DD) |

**Example response:**

```json
{
  "data": [
    {
      "period": "2025-12-18",
      "capacity_mw": 100032.4,
      "outage_mw": 3140.938,
      "percent_outage": 3.14
    }
  ],
  "count": 1,
  "total": 842,
  "offset": 0
}
```

### `GET /analytics`

Returns average monthly outage metrics grouped by year and month.

**Example response:**

```json
{
  "data": [
    {
      "year": 2026,
      "month": 3,
      "avg_outage_pct": 3.14,
      "avg_outage_mw": 3140.9,
      "avg_capacity_mw": 100032.4
    }
  ]
}
```

---

### `POST /refresh`

Triggers incremental data ingestion from the EIA API. Only fetches records newer than what is already stored.

**Example response:**

```json
{
  "run_id": "a1b2c3d4-...",
  "row_count": 42,
  "fact_outages": "data/processed/fact_outages.parquet",
  "dim_date": "data/processed/dim_date.parquet",
  "ingestion_log": "data/processed/ingestion_log.parquet"
}
```

---

## Data Model

Three Parquet files are written to `data/processed/`:

| Table | Description |
|---|---|
| `fact_outages` | Daily outage measurements (capacity, outage, percent) |
| `dim_date` | Date dimension derived from period (year, month, quarter, week, day) |
| `ingestion_log` | Record of each pipeline run |

See [docs/data_model.md](docs/data_model.md) and [docs/ER Diagram - Arkham Technologies coding challenge.pdf](docs/ER%20Diagram%20-%20Arkham%20Technologies%20coding%20challenge.pdf) for full schema details.

---

## Running Tests

```bash
pytest tests/
```

---

## Design Decisions

- **Parquet over CSV or SQLite** — Parquet is columnar and compressed, making it efficient for the kind of time-series filtering this API does (filter by date range, read only needed columns). It's also the format specified by the challenge.
- **Pandas over PySpark** — the dataset is small enough that pandas is the right tool. PySpark adds infrastructure complexity with no benefit at this scale.
- **Flat file storage over a database** — keeps the project self-contained with no external dependencies to set up. The `/refresh` endpoint writes to local Parquet files which the API reads directly.

---

## Assumptions

- Data is sourced at the US national level (not per plant) as provided by the EIA nuclear outages endpoint
- `period` is treated as the primary key — one record per day
- Incremental ingestion fetches from the day after the latest stored period (`latest_period + 1 day`), so each run only pulls genuinely new data with no overlap
- The frontend is intended for local use only and proxies API requests through Vite to avoid CORS issues in development
