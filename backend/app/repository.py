import pandas as pd
from backend.app.services.ingestion import FACT_OUTAGES_PATH, DIM_DATE_PATH

def get_outages(
        limit: int = 100,
        offset: int = 0,
        date_from: str | None = None,
        date_to: str | None = None,
) -> dict:
    if not FACT_OUTAGES_PATH.exists():
        return {"rows": [], "total": 0}

    df = pd.read_parquet(FACT_OUTAGES_PATH)

    if date_from:
        df = df[df["period"] >= date_from]
    if date_to:
        df = df[df["period"] <= date_to]

    df = df.sort_values("period", ascending=False)
    total = len(df)
    df = df.iloc[offset: offset + limit]

    return {"rows": df.to_dict(orient="records"), "total": total}


def get_monthly_analytics() -> list[dict]:
    if not FACT_OUTAGES_PATH.exists() or not DIM_DATE_PATH.exists():
        return []

    fact_df = pd.read_parquet(FACT_OUTAGES_PATH)
    dim_df = pd.read_parquet(DIM_DATE_PATH)

    merged = fact_df.merge(dim_df, on="period")
    monthly = merged.groupby(["year", "month"]).agg(
        avg_outage_pct=("percent_outage", "mean"),
        avg_outage_mw=("outage_mw", "mean"),
        avg_capacity_mw=("capacity_mw", "mean"),
    ).reset_index()

    monthly = monthly.sort_values(["year", "month"], ascending=False)
    return monthly.to_dict(orient="records")