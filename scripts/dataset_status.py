from __future__ import annotations
import csv, json
from collections import Counter
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SOURCE = PROJECT_ROOT / "data/raw/bengaluru_entities_v0.4.csv"

def main():
    with SOURCE.open(newline="", encoding="utf-8") as h:
        rows = list(csv.DictReader(h))

    report = {
        "entities": len(rows),
        "verification_status": dict(Counter(r["verification_status"] for r in rows)),
        "pronunciation_verified": sum(
            r["pronunciation_verified"].strip().lower() == "true" for r in rows
        ),
        "entity_types": dict(Counter(r["entity_type"] for r in rows)),
        "suffixes": dict(Counter(r["suffix"] or "(none)" for r in rows)),
        "source_types": dict(Counter(r["source_type"] or "(none)" for r in rows)),
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
