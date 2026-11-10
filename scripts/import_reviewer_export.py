from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from mapvoice_llm.railway_review_import import import_railway_reviews


def main() -> None:
    parser = argparse.ArgumentParser(description="Import mapvoice-review Railway CSV into MapVoice-LLM review events.")
    parser.add_argument("--input", required=True, help="CSV exported from /export/reviews.csv")
    parser.add_argument("--strict", action="store_true", help="Exit non-zero on invalid/unknown rows")
    args = parser.parse_args()

    result = import_railway_reviews(project_root=PROJECT_ROOT, review_csv=args.input)
    print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
    if args.strict and (result.invalid_rows or result.unknown_candidates):
        raise SystemExit(2)


if __name__ == "__main__":
    main()
