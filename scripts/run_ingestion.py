import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.app.services.ingestion import run_ingestion


def main() -> None:
    result = run_ingestion()
    print(f"Run ID : {result['run_id']}")
    print(f"Rows   : {result['row_count']}")
    print(f"Tables : {result['fact_outages']}, {result['dim_date']}, {result['ingestion_log']}")


if __name__ == "__main__":
    main()
