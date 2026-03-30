from __future__ import annotations

import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from backend.app.services.eia_client import EIAClient

DATA_DIR = Path("data/processed")
FACT_OUTAGES_PATH = DATA_DIR / "fact_outages.parquet"
DIM_DATE_PATH = DATA_DIR / "dim_date.parquet"
INGESTION_LOG_PATH = DATA_DIR / "ingestion_log.parquet"

PAGE_SIZE = 1000
REQUIRED_FIELDS = ["period", "capacity", "outage", "percentOutage"]

def get_latest_period() -> str | None:
    if not FACT_OUTAGES_PATH.exists():
        return None
    df = pd.read_parquet(FACT_OUTAGES_PATH)

    if df.empty:
        return None
    
    return df["period"].max()


def fetch_all_rows(page_size: int = PAGE_SIZE, start_date: str | None = None) -> list[dict[str, Any]]:
    client = EIAClient()
    all_rows: list[dict[str, Any]] = []
    offset = 0
    total: int | None = None

    while True:
        if total is not None:
            remaining = total - len(all_rows)
            if remaining <= 0:
                break
            length = min(page_size, remaining)
        else:
            length = page_size

        result = client.fetch_page(offset=offset, length=length, start_date=start_date)
        rows = result["rows"]

        if not rows:
            break

        all_rows.extend(rows)
        offset += len(rows)

        if total is None:
            total = result.get("total")

        if len(rows) < length:
            break

    return all_rows


def clean_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    cleaned_rows: list[dict[str, Any]] = []

    for row in rows:
        if any(field not in row for field in REQUIRED_FIELDS):
            continue

        try:
            cleaned_row = {
                "period": row["period"],
                "capacity_mw": float(row["capacity"]),
                "outage_mw": float(row["outage"]),
                "percent_outage": float(row["percentOutage"]),
            }
        except (TypeError, ValueError):
            continue

        cleaned_rows.append(cleaned_row)

    return cleaned_rows


def build_fact_outages(rows: list[dict[str, Any]]) -> pd.DataFrame:
    return pd.DataFrame(rows)


def build_dim_date(fact_df: pd.DataFrame) -> pd.DataFrame:
    # Derive date attributes from the period column for time-series queries
    dates = pd.to_datetime(fact_df["period"])
    return pd.DataFrame({
        "period": fact_df["period"],
        "year": dates.dt.year,
        "month": dates.dt.month,
        "quarter": dates.dt.quarter,
        "week": dates.dt.isocalendar().week.astype(int),
        "day_of_week": dates.dt.dayofweek,  # 0=Monday, 6=Sunday
    })


def append_ingestion_log(row_count: int) -> str:
    run_id = str(uuid.uuid4())
    new_entry = pd.DataFrame([{
        "run_id": run_id,
        "run_at": datetime.now(timezone.utc).isoformat(),
        "row_count": row_count,
        "source": "eia_api",
    }])

    # Append to existing log if it exists
    if INGESTION_LOG_PATH.exists():
        existing = pd.read_parquet(INGESTION_LOG_PATH)
        log_df = pd.concat([existing, new_entry], ignore_index=True)
    else:
        log_df = new_entry

    log_df.to_parquet(INGESTION_LOG_PATH, index=False)
    return run_id


def run_ingestion() -> dict[str, Any]:
    latest_period = get_latest_period()
    raw_rows = fetch_all_rows(start_date=latest_period)
    rows = clean_rows(raw_rows)

    if not rows:
        run_id = append_ingestion_log(0)
        return {
            "run_id": run_id,
            "row_count": 0,
            "fact_outages": str(FACT_OUTAGES_PATH),
            "dim_date": str(DIM_DATE_PATH),
            "ingestion_log": str(INGESTION_LOG_PATH),
        }

    fact_df = build_fact_outages(rows)
    dim_date_df = build_dim_date(fact_df)

    if FACT_OUTAGES_PATH.exists():
        existing = pd.read_parquet(FACT_OUTAGES_PATH)
        fact_df = pd.concat([existing, fact_df]).drop_duplicates(subset="period")

    if DIM_DATE_PATH.exists():
        existing = pd.read_parquet(DIM_DATE_PATH)
        dim_date_df = pd.concat([existing, dim_date_df]).drop_duplicates(subset="period")

    fact_df.to_parquet(FACT_OUTAGES_PATH, index=False)
    dim_date_df.to_parquet(DIM_DATE_PATH, index=False)
    run_id = append_ingestion_log(len(rows))

    return {
        "run_id": run_id,
        "row_count": len(rows),
        "fact_outages": str(FACT_OUTAGES_PATH),
        "dim_date": str(DIM_DATE_PATH),
        "ingestion_log": str(INGESTION_LOG_PATH),
    }
