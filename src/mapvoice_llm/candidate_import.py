from __future__ import annotations

import csv
import hashlib
from dataclasses import dataclass, asdict
from pathlib import Path

from .candidates import CandidateRepository
from .pack_context import PackContext


@dataclass(frozen=True)
class CandidateImportResult:
    pack_id: str
    source_rows: int
    imported: int
    skipped_existing_entity: int
    skipped_existing_candidate: int
    skipped_missing_name: int
    destination: str

    def to_dict(self) -> dict:
        return asdict(self)


def _stable_candidate_id(
    pack_id: str,
    latin_name: str,
) -> str:
    digest = hashlib.sha1(
        f"{pack_id}:{latin_name.casefold()}".encode(
            "utf-8"
        )
    ).hexdigest()[:12]
    prefix = pack_id.replace("-", "_")
    return f"{prefix}_import_{digest}"


def import_candidates(
    *,
    context: PackContext,
    source_csv: str | Path,
) -> CandidateImportResult:
    source_csv = Path(source_csv)

    with source_csv.open(
        newline="",
        encoding="utf-8",
    ) as handle:
        source_rows = list(
            csv.DictReader(handle)
        )

    if context.candidate_csv is None:
        raise RuntimeError(
            "Regional pack has no candidate file"
        )

    entity_names = {
        entity.latin_name.strip().casefold()
        for entity in (
            context.entity_repository.list()
        )
        if entity.latin_name.strip()
    }

    candidate_repo = CandidateRepository(
        context.candidate_csv
    )
    existing_candidates = (
        candidate_repo.list(limit=100000)
    )
    candidate_names = {
        (
            row.get("latin_name")
            or row.get("english_name")
            or ""
        ).strip().casefold()
        for row in existing_candidates
    }

    with context.candidate_csv.open(
        newline="",
        encoding="utf-8",
    ) as handle:
        reader = csv.DictReader(handle)
        fieldnames = list(
            reader.fieldnames or []
        )

    imported = []
    skipped_entity = 0
    skipped_candidate = 0
    skipped_missing = 0

    for row in source_rows:
        latin_name = (
            row.get("latin_name")
            or row.get("english_name")
            or row.get("name")
            or ""
        ).strip()

        if not latin_name:
            skipped_missing += 1
            continue

        key = latin_name.casefold()
        if key in entity_names:
            skipped_entity += 1
            continue
        if key in candidate_names:
            skipped_candidate += 1
            continue

        imported.append({
            "candidate_id": (
                row.get("candidate_id")
                or _stable_candidate_id(
                    context.pack.pack_id,
                    latin_name,
                )
            ),
            "latin_name": latin_name,
            "entity_type": (
                row.get("entity_type")
                or "locality"
            ),
            "city": context.pack.city,
            "region_language": (
                context.pack.region_language
            ),
            "region_language_code": (
                context.pack.region_language_code
            ),
            "annotation_status": (
                row.get(
                    "annotation_status",
                    "candidate",
                )
                or "candidate"
            ),
            "native_name": (
                row.get("native_name")
                or ""
            ).strip(),
            "source_name": (
                row.get("source_name")
                or ""
            ).strip(),
            "source_url": (
                row.get("source_url")
                or ""
            ).strip(),
            "notes": (
                row.get("notes")
                or "Imported candidate; review required."
            ).strip(),
        })
        candidate_names.add(key)

    if imported:
        with context.candidate_csv.open(
            "a",
            newline="",
            encoding="utf-8",
        ) as handle:
            writer = csv.DictWriter(
                handle,
                fieldnames=fieldnames,
            )
            for row in imported:
                writer.writerow({
                    key: row.get(key, "")
                    for key in fieldnames
                })

    return CandidateImportResult(
        pack_id=context.pack.pack_id,
        source_rows=len(source_rows),
        imported=len(imported),
        skipped_existing_entity=(
            skipped_entity
        ),
        skipped_existing_candidate=(
            skipped_candidate
        ),
        skipped_missing_name=(
            skipped_missing
        ),
        destination=str(
            context.candidate_csv
        ),
    )
