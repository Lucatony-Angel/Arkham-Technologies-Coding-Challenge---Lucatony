# Data Model

## Overview
This schema stores daily US nuclear outage readings from the EIA API across 3 tables.

---

## Tables

### `dim_date`
Date dimension used for time-series filtering and grouping.

| Column | Type | Constraints |
|---|---|---|
| period | varchar | Primary Key |
| year | integer | |
| month | integer | |
| quarter | integer | |
| week | integer | |
| day_of_week | integer | |

### `fact_outages`
Daily outage measurements from the EIA API.

| Column | Type | Constraints |
|---|---|---|
| period | varchar | Primary Key, FK → dim_date.period |
| capacity_mw | float | |
| outage_mw | float | |
| percent_outage | float | |

### `ingestion_log`
Tracks each pipeline run.

| Column | Type | Constraints |
|---|---|---|
| run_id | varchar | Primary Key |
| run_at | varchar | |
| row_count | integer | |
| source | varchar | |

---

## Relationships

- `fact_outages.period` → `dim_date.period` (many-to-one): each outage reading maps to one date record
- `ingestion_log` is standalone — no foreign keys

---

---

## Aggregation Example

**Question: What is the average nuclear outage rate per month?**

This is a real operational question — energy analysts use monthly outage trends to assess grid reliability and plan capacity.

By joining `fact_outages` with `dim_date` on `period`, we can group by year and month to compute average outage metrics:

```python
import pandas as pd

df = pd.read_parquet("data/processed/fact_outages.parquet")
dim = pd.read_parquet("data/processed/dim_date.parquet")

merged = df.merge(dim, on="period")
monthly = merged.groupby(["year", "month"]).agg(
    avg_outage_pct=("percent_outage", "mean"),
    avg_outage_mw=("outage_mw", "mean"),
).reset_index()

print(monthly)
```

**Example output:**

| year | month | avg_outage_pct | avg_outage_mw |
|---|---|---|---|
| 2025 | 11 | 4.21 | 4218.3 |
| 2025 | 12 | 3.14 | 3140.9 |
| 2026 | 1 | 5.02 | 5024.1 |

This is why `dim_date` exists — it makes grouping by time period straightforward without parsing date strings in every query.

---

## ER Diagram
See `docs/ER Diagram - Arkham Technologies coding challenge.pdf`.
