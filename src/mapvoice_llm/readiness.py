from __future__ import annotations

import csv
from pathlib import Path


def training_readiness(entity_csv: str | Path, candidate_csv: str | Path) -> dict:
    entity_csv = Path(entity_csv)
    candidate_csv = Path(candidate_csv)

    with entity_csv.open(newline="", encoding="utf-8") as handle:
        entities = list(csv.DictReader(handle))

    with candidate_csv.open(newline="", encoding="utf-8") as handle:
        candidates = list(csv.DictReader(handle))

    verified_entities = [
        row for row in entities
        if row.get("verification_status", "").strip().lower() == "verified"
    ]
    pronunciation_verified = [
        row for row in entities
        if row.get("pronunciation_verified", "").strip().lower() == "true"
    ]
    reviewed_candidates = [
        row for row in candidates
        if row.get("annotation_status") == "reviewed"
    ]
    promotable_candidates = [
        row for row in reviewed_candidates
        if row.get("kannada_name", "").strip()
        and row.get("source_name", "").strip()
    ]

    gates = {
        "minimum_50_verified_entities": len(verified_entities) >= 50,
        "minimum_25_pronunciation_verified": len(pronunciation_verified) >= 25,
        "minimum_3_entity_types": len({
            row.get("entity_type") for row in verified_entities if row.get("entity_type")
        }) >= 3,
        "no_unreviewed_promotable_candidates": len(promotable_candidates) == 0,
    }

    return {
        "entities_total": len(entities),
        "entities_verified": len(verified_entities),
        "pronunciation_verified": len(pronunciation_verified),
        "candidates_total": len(candidates),
        "candidates_reviewed": len(reviewed_candidates),
        "candidates_promotable": len(promotable_candidates),
        "gates": gates,
        "ready_for_first_strict_training": (
            gates["minimum_50_verified_entities"]
            and gates["minimum_25_pronunciation_verified"]
            and gates["minimum_3_entity_types"]
        ),
    }
