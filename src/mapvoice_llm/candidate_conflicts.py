from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path

from .candidate_normalization import normalize_name


def audit_candidate_conflicts(
    candidate_csv: str | Path,
) -> dict:
    candidate_csv = Path(candidate_csv)

    with candidate_csv.open(
        newline="",
        encoding="utf-8",
    ) as handle:
        rows = list(csv.DictReader(handle))

    by_name = defaultdict(list)
    for row in rows:
        latin = (
            row.get("latin_name")
            or row.get("english_name")
            or ""
        )
        key = normalize_name(latin)
        if key:
            by_name[key].append(row)

    duplicates = []
    native_conflicts = []
    source_conflicts = []

    for key, group in by_name.items():
        if len(group) <= 1:
            continue

        duplicates.append({
            "normalized_name": key,
            "candidate_ids": [
                row.get("candidate_id", "")
                for row in group
            ],
            "sources": sorted({
                row.get("source_id", "")
                for row in group
                if row.get("source_id", "")
            }),
        })

        native_names = {
            (
                row.get("native_name")
                or row.get("kannada_name")
                or ""
            ).strip()
            for row in group
            if (
                row.get("native_name")
                or row.get("kannada_name")
                or ""
            ).strip()
        }
        if len(native_names) > 1:
            native_conflicts.append({
                "normalized_name": key,
                "native_names": sorted(native_names),
                "candidate_ids": [
                    row.get("candidate_id", "")
                    for row in group
                ],
            })

        record_ids = {
            (
                row.get("source_id", ""),
                row.get("source_record_id", ""),
            )
            for row in group
            if row.get("source_id", "")
        }
        if len(record_ids) > 1:
            source_conflicts.append({
                "normalized_name": key,
                "source_records": [
                    {
                        "source_id": source_id,
                        "source_record_id": record_id,
                    }
                    for source_id, record_id in sorted(record_ids)
                ],
            })

    return {
        "rows": len(rows),
        "duplicate_name_groups": len(duplicates),
        "native_name_conflicts": len(native_conflicts),
        "multi_source_name_groups": len(source_conflicts),
        "duplicates": duplicates,
        "native_conflicts": native_conflicts,
        "source_conflicts": source_conflicts,
    }
