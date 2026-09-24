from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SOURCE = PROJECT_ROOT / "data" / "seeds" / "bengaluru_candidates_v0.6.csv"


def main() -> None:
    with SOURCE.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))

    report = {
        "candidates": len(rows),
        "annotation_status": dict(
            Counter(row["annotation_status"] for row in rows)
        ),
        "entity_types": dict(
            Counter(row["entity_type"] for row in rows)
        ),
        "with_kannada_name": sum(
            bool(row["kannada_name"].strip()) for row in rows
        ),
        "with_source": sum(
            bool(row["source_name"].strip()) for row in rows
        ),
    }

    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
