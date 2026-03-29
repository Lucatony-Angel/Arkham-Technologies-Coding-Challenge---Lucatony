import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.app.services.ingestion import run_ingestion


def main() -> None:
    result = run_ingestion()
    print(f"Wrote {result['row_count']} rows to {result['output_path']}")


if __name__ == "__main__":
    main()
