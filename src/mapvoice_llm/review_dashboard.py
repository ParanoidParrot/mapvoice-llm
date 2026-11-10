from __future__ import annotations

import csv
from pathlib import Path

from .pack_context import load_pack_context
from .regional_packs import RegionalPackRegistry
from .review_analytics import summarize_pack_candidates
from .review_store import ReviewStore


def review_progress(
    project_root: str | Path,
    *,
    pack_id: str | None = None,
    include_details: bool = False,
) -> dict:
    project_root = Path(project_root)

    registry = RegionalPackRegistry(
        project_root / "configs" / "regional_packs.json"
    )

    packs = []

    for pack in registry.list():
        if pack_id and pack.pack_id != pack_id:
            continue

        context = load_pack_context(project_root, pack.pack_id)
        if context.candidate_csv is None or not context.candidate_csv.exists():
            continue

        with context.candidate_csv.open(newline="", encoding="utf-8") as handle:
            candidates = list(csv.DictReader(handle))

        store = ReviewStore(project_root, pack.pack_id)
        events = store.list()
        by_candidate: dict[str, list[dict]] = {}
        for event in events:
            by_candidate.setdefault(event["candidate_id"], []).append(event)

        summary = summarize_pack_candidates(candidates, by_candidate)
        details = summary.pop("details")
        row = {
            "pack_id": pack.pack_id,
            "city": pack.city,
            "language": pack.region_language,
            "review_events": len(events),
            **summary,
        }
        # Backward-compatible field used by earlier tooling.
        row["verified"] = row["materialization_ready"]
        if include_details:
            row["candidate_details"] = details
        packs.append(row)

    return {
        "packs": packs,
        "totals": {
            "candidates": sum(row["candidates"] for row in packs),
            "reviewed_candidates": sum(row["reviewed_candidates"] for row in packs),
            "independent_reviews": sum(row["independent_reviews"] for row in packs),
            "disagreements": sum(row["disagreements"] for row in packs),
            "adjudication_ready": sum(row["adjudication_ready"] for row in packs),
            "materialization_ready": sum(row["materialization_ready"] for row in packs),
            "pronunciation_ready": sum(row["pronunciation_ready"] for row in packs),
        },
        # Backward-compatible top-level field.
        "verified_total": sum(row["materialization_ready"] for row in packs),
    }
