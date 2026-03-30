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
  "count": 100,
  "offset": 0
}
```

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

## Assumptions

- Data is sourced at the US national level (not per plant) as provided by the EIA nuclear outages endpoint
- `period` is treated as the primary key — one record per day
- Incremental ingestion uses the most recent stored period as the start date filter, with `drop_duplicates` as a safeguard against overlap
- The frontend is intended for local use only and proxies API requests through Vite to avoid CORS issues in development
