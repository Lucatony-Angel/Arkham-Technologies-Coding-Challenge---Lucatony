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

## ER Diagram
See `docs/er_diagram.pdf`.
