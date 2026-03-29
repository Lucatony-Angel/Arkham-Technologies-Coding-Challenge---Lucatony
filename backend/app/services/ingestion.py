from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from backend.app.services.eia_client import EIAClient

OUTPUT_PATH = Path("data/raw/us_nuclear_outages.parquet")
PAGE_SIZE = 1000
REQUIRED_FIELDS = ["period", "capacity", "outage", "percentOutage"]

def fetch_all_rows(page_size: int = PAGE_SIZE) -> list[dict[str, Any]]:
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

        result = client.fetch_page(offset=offset, length=length)
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
                "capacity": float(row["capacity"]),
                "outage": float(row["outage"]),
                "percentOutage": float(row["percentOutage"]),
            }
        except (TypeError, ValueError):
            continue

        cleaned_rows.append(cleaned_row)

    return cleaned_rows

def run_ingestion(output_path: Path = OUTPUT_PATH) -> dict[str, Any]:
    raw_rows = fetch_all_rows()
    rows = clean_rows(raw_rows)

    if not rows:
        raise RuntimeError("No valid outage rows were collected during ingestion")
    
    output_path.parent.mkdir(parents = True, exist_ok = True)

    df = pd.DataFrame(rows)
    df.to_parquet(output_path, index = False)

    return {
        "row_count": len(rows),
        "output_path": str(output_path),
    }