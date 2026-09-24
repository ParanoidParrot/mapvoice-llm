from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path


def dataset_status(entity_csv: str | Path) -> dict:
    entity_csv = Path(entity_csv)

    if not entity_csv.exists():
        return {
            "entities": 0,
            "verified": 0,
            "pronunciation_verified": 0,
            "entity_types": {},
            "dataset_file": str(entity_csv),
        }

    with entity_csv.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))

    return {
        "entities": len(rows),
        "verified": sum(
            row.get("verification_status", "").strip().lower() == "verified"
            for row in rows
        ),
        "pronunciation_verified": sum(
            row.get("pronunciation_verified", "").strip().lower() == "true"
            for row in rows
        ),
        "entity_types": dict(
            Counter(row.get("entity_type", "unknown") for row in rows)
        ),
        "dataset_file": entity_csv.name,
    }
