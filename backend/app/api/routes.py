from datetime import date
from fastapi import APIRouter, HTTPException, Query
from backend.app.repository import get_outages
from backend.app.services.ingestion import run_ingestion

router = APIRouter()

@router.get("/data")
def data(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    date_from: date | None = Query(None),
    date_to: date | None = Query(None),
):
    result = get_outages(
        limit=limit,
        offset=offset,
        date_from=date_from.isoformat() if date_from else None,
        date_to=date_to.isoformat() if date_to else None,
    )
    return {"data": result["rows"], "count": len(result["rows"]), "total": result["total"], "offset": offset}

@router.post("/refresh")
def refresh():
    try:
        result = run_ingestion()
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=502, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="An unexpected error occurred")