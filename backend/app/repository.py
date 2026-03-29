import pandas as pd
from backend.app.services.ingestion import FACT_OUTAGES_PATH

def get_outages(
        limit: int = 100,
        offset: int = 0,
        date_from: str | None = None,
        date_to: str | None = None,
) -> list[dict]:
    if not FACT_OUTAGES_PATH.exists():
        return []
    
    df = pd.read_parquet(FACT_OUTAGES_PATH)

    if date_from:
        df = df[df["period"] >= date_from]
    if date_to:
        df = df[df["period"] <= date_to]

    df = df.sort_values("period", ascending=False)
    df = df.iloc[offset: offset + limit]

    return df.to_dict(orient="records")