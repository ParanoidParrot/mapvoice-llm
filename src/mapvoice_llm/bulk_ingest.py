from __future__ import annotations
import csv
import json
from datetime import datetime, timezone
from pathlib import Path

from .candidate_normalization import normalize_name, coordinate_key
from .ingestion_manifest import sha256_file, write_ingestion_manifest
from .pack_context import PackContext
from .provenance import score_candidate
from .source_registry import SourceDefinition

def _existing_keys(context: PackContext) -> tuple[set[str], set[str]]:
    entity_names = {
        normalize_name(e.latin_name)
        for e in context.entity_repository.list()
        if e.latin_name
    }

    candidate_names: set[str] = set()
    candidate_ids: set[str] = set()

    if context.candidate_csv and context.candidate_csv.exists():
        with context.candidate_csv.open(newline="", encoding="utf-8") as handle:
            for row in csv.DictReader(handle):
                name = row.get("latin_name") or row.get("english_name") or ""
                candidate_names.add(normalize_name(name))
                if row.get("candidate_id"):
                    candidate_ids.add(row["candidate_id"])

    return entity_names | candidate_names, candidate_ids

def _stable_id(pack_id: str, source_id: str, source_record_id: str, latin_name: str) -> str:
    import hashlib
    raw = f"{pack_id}|{source_id}|{source_record_id}|{normalize_name(latin_name)}"
    return f"{pack_id.replace('-', '_')}_src_{hashlib.sha1(raw.encode()).hexdigest()[:12]}"

def _coerce_candidate(
    row: dict,
    *,
    context: PackContext,
    source: SourceDefinition,
    snapshot_hash: str,
    retrieved_at: str,
) -> dict | None:
    latin_name = (
        row.get("latin_name")
        or row.get("english_name")
        or row.get("name")
        or ""
    ).strip()
    if not latin_name:
        return None

    source_record_id = str(
        row.get("source_record_id")
        or row.get("osm_id")
        or row.get("@id")
        or row.get("id")
        or normalize_name(latin_name)
    )

    out = {
        "candidate_id": _stable_id(
            context.pack.pack_id,
            source.source_id,
            source_record_id,
            latin_name,
        ),
        "latin_name": latin_name,
        "entity_type": (row.get("entity_type") or row.get("place") or "locality").strip(),
        "city": context.pack.city,
        "region_language": context.pack.region_language,
        "region_language_code": context.pack.region_language_code,
        "annotation_status": "candidate",
        "native_name": (row.get("native_name") or "").strip(),
        "alternate_names": (row.get("alternate_names") or "").strip(),
        "latitude": str(row.get("latitude") or row.get("lat") or "").strip(),
        "longitude": str(row.get("longitude") or row.get("lon") or "").strip(),
        "source_id": source.source_id,
        "source_record_id": source_record_id,
        "source_name": source.label,
        "source_url": (row.get("source_url") or source.homepage or "").strip(),
        "source_license": source.license,
        "source_retrieved_at": retrieved_at,
        "source_snapshot_sha256": snapshot_hash,
        "provenance_status": "",
        "review_priority": "",
        "notes": (row.get("notes") or "").strip(),
    }

    score = score_candidate(out)
    out["provenance_status"] = score.status
    # Higher priority means "review sooner".
    out["review_priority"] = str(max(1, 100 - score.score))
    return out

def ingest_rows(
    *,
    project_root: Path,
    context: PackContext,
    source: SourceDefinition,
    input_path: Path,
    rows: list[dict],
) -> dict:
    if context.pack.pack_id not in source.allowed_pack_ids:
        raise ValueError(
            f"Source {source.source_id} is not approved for pack {context.pack.pack_id}"
        )
    if context.candidate_csv is None:
        raise RuntimeError("Pack has no candidate CSV")

    existing_names, existing_ids = _existing_keys(context)
    snapshot_hash = sha256_file(input_path)
    retrieved_at = datetime.now(timezone.utc).isoformat()

    with context.candidate_csv.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        fieldnames = list(reader.fieldnames or [])

    accepted = []
    skipped_duplicate = 0
    skipped_missing_name = 0

    for row in rows:
        candidate = _coerce_candidate(
            row,
            context=context,
            source=source,
            snapshot_hash=snapshot_hash,
            retrieved_at=retrieved_at,
        )
        if candidate is None:
            skipped_missing_name += 1
            continue

        key = normalize_name(candidate["latin_name"])
        if key in existing_names or candidate["candidate_id"] in existing_ids:
            skipped_duplicate += 1
            continue

        accepted.append(candidate)
        existing_names.add(key)
        existing_ids.add(candidate["candidate_id"])

    if accepted:
        with context.candidate_csv.open("a", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            for row in accepted:
                writer.writerow({field: row.get(field, "") for field in fieldnames})

    stats = {
        "input_rows": len(rows),
        "accepted": len(accepted),
        "skipped_duplicate": skipped_duplicate,
        "skipped_missing_name": skipped_missing_name,
    }
    manifest = write_ingestion_manifest(
        project_root=project_root,
        pack_id=context.pack.pack_id,
        source_id=source.source_id,
        input_path=input_path,
        stats=stats,
    )
    return {**stats, "manifest": str(manifest.relative_to(project_root))}
