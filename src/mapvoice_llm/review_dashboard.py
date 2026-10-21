from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

from .pack_context import load_pack_context
from .regional_packs import RegionalPackRegistry
from .review_consensus import resolve_candidate_reviews
from .review_store import ReviewStore


def review_progress(
    project_root: str | Path,
) -> dict:
    project_root = Path(
        project_root
    )

    registry = RegionalPackRegistry(
        project_root
        / "configs"
        / "regional_packs.json"
    )

    packs = []

    for pack in registry.list():
        context = load_pack_context(
            project_root,
            pack.pack_id,
        )

        if (
            context.candidate_csv
            is None
            or not context.candidate_csv.exists()
        ):
            continue

        with context.candidate_csv.open(
            newline="",
            encoding="utf-8",
        ) as handle:
            candidates = list(
                csv.DictReader(handle)
            )

        store = ReviewStore(
            project_root,
            pack.pack_id,
        )

        by_candidate = {}
        events = store.list()

        for event in events:
            by_candidate.setdefault(
                event["candidate_id"],
                [],
            ).append(event)

        statuses = Counter()

        for candidate in candidates:
            result = (
                resolve_candidate_reviews(
                    by_candidate.get(
                        candidate[
                            "candidate_id"
                        ],
                        [],
                    )
                )
            )
            statuses[
                result["status"]
            ] += 1

        packs.append({
            "pack_id": pack.pack_id,
            "city": pack.city,
            "language": (
                pack.region_language
            ),
            "candidates": (
                len(candidates)
            ),
            "review_events": (
                len(events)
            ),
            "statuses": (
                dict(statuses)
            ),
            "verified": (
                statuses.get(
                    "verified",
                    0,
                )
            ),
        })

    return {
        "packs": packs,
        "verified_total": sum(
            row["verified"]
            for row in packs
        ),
    }
