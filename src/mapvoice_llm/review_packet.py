from __future__ import annotations

import csv
from pathlib import Path

from .provenance import score_candidate
from .review_consensus import resolve_candidate_reviews
from .review_store import ReviewStore


FIELDS = [
    "candidate_id",
    "latin_name",
    "native_name",
    "entity_type",
    "source_name",
    "source_url",
    "source_license",
    "source_record_id",
    "latitude",
    "longitude",
    "provenance_score",
    "provenance_status",
    "review_status",
    "independent_reviewers",
    "requires_adjudication",
    "decision",
    "reviewer_native_name",
    "source_approved",
    "pronunciation_approved",
    "review_notes",
]


def build_review_packet(
    *,
    project_root: str | Path,
    pack_id: str,
    candidate_csv: str | Path,
    output: str | Path,
) -> dict:
    project_root = Path(project_root)
    candidate_csv = Path(candidate_csv)
    output = Path(output)

    with candidate_csv.open(
        newline="",
        encoding="utf-8",
    ) as handle:
        rows = list(csv.DictReader(handle))

    store = ReviewStore(
        project_root,
        pack_id,
    )

    by_candidate: dict[str, list[dict]] = {}
    for event in store.list():
        by_candidate.setdefault(
            event["candidate_id"],
            [],
        ).append(event)

    packet_rows = []

    for row in rows:
        candidate_id = row["candidate_id"]
        consensus = resolve_candidate_reviews(
            by_candidate.get(candidate_id, [])
        )
        provenance = score_candidate(row)

        packet_rows.append({
            "candidate_id": candidate_id,
            "latin_name": row.get("latin_name") or row.get("english_name") or "",
            "native_name": row.get("native_name") or row.get("kannada_name") or "",
            "entity_type": row.get("entity_type", ""),
            "source_name": row.get("source_name", ""),
            "source_url": row.get("source_url", ""),
            "source_license": row.get("source_license", ""),
            "source_record_id": row.get("source_record_id", ""),
            "latitude": row.get("latitude", ""),
            "longitude": row.get("longitude", ""),
            "provenance_score": provenance.score,
            "provenance_status": provenance.status,
            "review_status": consensus["status"],
            "independent_reviewers": consensus["independent_reviewers"],
            "requires_adjudication": consensus["requires_adjudication"],
            "decision": "",
            "reviewer_native_name": "",
            "source_approved": "",
            "pronunciation_approved": "",
            "review_notes": "",
        })

    packet_rows.sort(
        key=lambda row: (
            0 if row["native_name"] else 1,
            -int(row["provenance_score"]),
            row["latin_name"].casefold(),
        )
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
            fieldnames=FIELDS,
        )
        writer.writeheader()
        writer.writerows(packet_rows)

    return {
        "pack_id": pack_id,
        "rows": len(packet_rows),
        "output": str(output.relative_to(project_root)),
    }
