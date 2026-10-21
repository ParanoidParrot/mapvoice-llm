from __future__ import annotations

import csv
from dataclasses import dataclass, asdict
from pathlib import Path

from .review_models import ReviewEvent
from .review_store import ReviewStore


TRUE_VALUES = {"1", "true", "yes", "y", "approved"}


@dataclass(frozen=True)
class ReviewPacketImportResult:
    pack_id: str
    reviewer_id: str
    rows_seen: int
    events_appended: int
    skipped_blank_decision: int
    skipped_invalid_decision: int
    duplicate_existing_review: int

    def to_dict(self) -> dict:
        return asdict(self)


def _bool(value: str | None) -> bool:
    return str(value or "").strip().casefold() in TRUE_VALUES


def import_review_packet(
    *,
    project_root: str | Path,
    pack_id: str,
    reviewer_id: str,
    packet_csv: str | Path,
    stage: str = "independent",
) -> ReviewPacketImportResult:
    packet_csv = Path(packet_csv)

    with packet_csv.open(
        newline="",
        encoding="utf-8",
    ) as handle:
        rows = list(csv.DictReader(handle))

    store = ReviewStore(project_root, pack_id)
    existing = store.list()

    existing_keys = {
        (
            event["candidate_id"],
            event["reviewer_id"],
            event["stage"],
        )
        for event in existing
    }

    appended = 0
    skipped_blank = 0
    skipped_invalid = 0
    duplicate = 0

    for row in rows:
        candidate_id = (
            row.get("candidate_id")
            or ""
        ).strip()
        decision = (
            row.get("decision")
            or row.get("review_decision")
            or ""
        ).strip().casefold()

        if not candidate_id or not decision:
            skipped_blank += 1
            continue

        if decision not in {
            "approve",
            "reject",
            "needs-correction",
        }:
            skipped_invalid += 1
            continue

        key = (
            candidate_id,
            reviewer_id,
            stage,
        )
        if key in existing_keys:
            duplicate += 1
            continue

        native_name = (
            row.get("reviewer_native_name")
            or row.get("native_name")
            or ""
        ).strip()

        event = ReviewEvent.create(
            candidate_id=candidate_id,
            reviewer_id=reviewer_id,
            stage=stage,
            decision=decision,
            native_name=native_name,
            source_approved=_bool(
                row.get("source_approved")
            ),
            pronunciation_approved=_bool(
                row.get(
                    "pronunciation_approved"
                )
            ),
            notes=(
                row.get("review_notes")
                or ""
            ),
        )

        store.append(event)
        existing_keys.add(key)
        appended += 1

    return ReviewPacketImportResult(
        pack_id=pack_id,
        reviewer_id=reviewer_id,
        rows_seen=len(rows),
        events_appended=appended,
        skipped_blank_decision=skipped_blank,
        skipped_invalid_decision=skipped_invalid,
        duplicate_existing_review=duplicate,
    )
