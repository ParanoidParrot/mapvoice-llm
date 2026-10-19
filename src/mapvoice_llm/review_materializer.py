from __future__ import annotations

import csv
from pathlib import Path

from .review_consensus import (
    resolve_candidate_reviews,
)
from .review_store import ReviewStore


REVIEWED_ENTITY_FIELDS = [
    "entity_id",
    "latin_name",
    "native_name",
    "entity_type",
    "city",
    "language",
    "language_code",
    "alternate_spellings",
    "morphemes",
    "suffix",
    "verification_status",
    "pronunciation_verified",
    "source_name",
    "source_url",
    "source_type",
    "reviewer",
    "notes",
]


def materialize_reviewed_entities(
    *,
    project_root: str | Path,
    pack,
    candidate_csv: str | Path,
) -> dict:
    project_root = Path(
        project_root
    )
    candidate_csv = Path(
        candidate_csv
    )

    with candidate_csv.open(
        newline="",
        encoding="utf-8",
    ) as handle:
        candidates = list(
            csv.DictReader(
                handle
            )
        )

    store = ReviewStore(
        project_root,
        pack.pack_id,
    )

    by_candidate: dict[
        str,
        list[dict],
    ] = {}

    for event in store.list():
        by_candidate.setdefault(
            event["candidate_id"],
            [],
        ).append(event)

    rows = []
    status_counts: dict[
        str,
        int,
    ] = {}

    for candidate in candidates:
        candidate_id = (
            candidate[
                "candidate_id"
            ]
        )
        consensus = (
            resolve_candidate_reviews(
                by_candidate.get(
                    candidate_id,
                    [],
                )
            )
        )

        status = consensus[
            "status"
        ]
        status_counts[status] = (
            status_counts.get(
                status,
                0,
            )
            + 1
        )

        if status != "verified":
            continue

        entity_id = (
            f"{pack.pack_id.replace('-', '_')}_rev_"
            + candidate_id.split(
                "_"
            )[-1]
        )

        reviewer_ids = sorted({
            event[
                "reviewer_id"
            ]
            for event in (
                by_candidate.get(
                    candidate_id,
                    [],
                )
            )
        })

        rows.append({
            "entity_id": entity_id,
            "latin_name": (
                candidate.get(
                    "latin_name"
                )
                or candidate.get(
                    "english_name"
                )
                or ""
            ),
            "native_name": (
                consensus[
                    "native_name"
                ]
            ),
            "entity_type": (
                candidate.get(
                    "entity_type",
                    "locality",
                )
            ),
            "city": pack.city,
            "language": (
                pack.region_language
            ),
            "language_code": (
                pack.region_language_code
            ),
            "alternate_spellings": (
                candidate.get(
                    "alternate_names",
                    "",
                )
            ),
            "morphemes": "",
            "suffix": "",
            "verification_status": (
                "verified"
            ),
            "pronunciation_verified": (
                "true"
                if consensus[
                    "pronunciation_verified"
                ]
                else "false"
            ),
            "source_name": (
                candidate.get(
                    "source_name",
                    "",
                )
            ),
            "source_url": (
                candidate.get(
                    "source_url",
                    "",
                )
            ),
            "source_type": (
                candidate.get(
                    "source_id",
                    "",
                )
            ),
            "reviewer": (
                "|".join(
                    reviewer_ids
                )
            ),
            "notes": (
                "Materialized from "
                f"candidate {candidate_id}; "
                "independent_reviewers="
                f"{consensus['independent_reviewers']}; "
                "adjudicated="
                f"{consensus['adjudicated']}"
            ),
        })

    output = (
        project_root
        / "data"
        / "reviewed"
        / pack.pack_id
        / "entities.csv"
    )
    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with output.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=(
                REVIEWED_ENTITY_FIELDS
            ),
        )
        writer.writeheader()
        writer.writerows(rows)

    return {
        "pack_id": pack.pack_id,
        "reviewed_entities": (
            len(rows)
        ),
        "candidate_status_counts": (
            status_counts
        ),
        "output": str(
            output.relative_to(
                project_root
            )
        ),
    }
