from __future__ import annotations

import csv
import json
import re
from dataclasses import dataclass, asdict
from pathlib import Path

from .pack_context import load_pack_context
from .regional_packs import RegionalPackRegistry
from .review_models import ReviewEvent
from .review_store import ReviewStore

REQUIRED_COLUMNS = {
    "review_id", "candidate_id", "reviewer_id", "language_code", "latin_name",
    "suggested_native_name", "corrected_native_name", "spelling_status",
    "pronunciation_status", "place_familiarity", "notes", "created_at",
}
VALID_SPELLING = {"correct", "incorrect", "unsure"}
VALID_PRONUNCIATION = {"correct", "incorrect", "unsure", "not_applicable"}
VALID_FAMILIARITY = {"know", "heard_of", "unknown"}


@dataclass(frozen=True)
class RailwayReviewImportResult:
    rows_seen: int = 0
    events_appended: int = 0
    duplicate_review_id: int = 0
    invalid_rows: int = 0
    unknown_candidates: int = 0
    packs_touched: tuple[str, ...] = ()
    errors: tuple[str, ...] = ()

    def to_dict(self) -> dict:
        d = asdict(self)
        d["packs_touched"] = list(self.packs_touched)
        d["errors"] = list(self.errors)
        return d


def _norm(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", (value or "").casefold())


def _load_candidates(project_root: Path, pack_id: str) -> tuple[dict[str, dict], dict[str, list[dict]]]:
    context = load_pack_context(project_root, pack_id)
    if context.candidate_csv is None or not context.candidate_csv.exists():
        return {}, {}
    with context.candidate_csv.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    by_id = {row.get("candidate_id", "").strip(): row for row in rows if row.get("candidate_id")}
    by_name: dict[str, list[dict]] = {}
    for row in rows:
        name = row.get("latin_name") or row.get("english_name") or ""
        by_name.setdefault(_norm(name), []).append(row)
    return by_id, by_name


def _pack_map(project_root: Path) -> dict[str, str]:
    registry = RegionalPackRegistry(project_root / "configs" / "regional_packs.json")
    return {pack.region_language_code: pack.pack_id for pack in registry.list()}


def _map_semantics(row: dict) -> tuple[str, str, bool, bool]:
    spelling = row["spelling_status"].strip().casefold()
    pronunciation = row["pronunciation_status"].strip().casefold()
    suggested = row.get("suggested_native_name", "").strip()
    corrected = row.get("corrected_native_name", "").strip()

    if spelling == "correct":
        decision = "approve"
        native_name = corrected or suggested
        spelling_approved = True
    else:
        decision = "needs-correction"
        native_name = corrected or suggested
        spelling_approved = False

    pronunciation_approved = pronunciation == "correct"
    # The legacy field is used by consensus as the human approval gate.
    # Preserve the richer Railway spelling status in event metadata below.
    source_approved = spelling_approved
    return decision, native_name, pronunciation_approved, source_approved


def import_railway_reviews(*, project_root: str | Path, review_csv: str | Path) -> RailwayReviewImportResult:
    project_root = Path(project_root)
    review_csv = Path(review_csv)
    with review_csv.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        missing = REQUIRED_COLUMNS - set(reader.fieldnames or [])
        if missing:
            raise ValueError("Missing Railway review columns: " + ", ".join(sorted(missing)))
        rows = list(reader)

    lang_to_pack = _pack_map(project_root)
    candidate_cache: dict[str, tuple[dict[str, dict], dict[str, list[dict]]]] = {}
    store_cache: dict[str, ReviewStore] = {}
    existing_review_ids: set[str] = set()
    for pack_id in set(lang_to_pack.values()):
        store = ReviewStore(project_root, pack_id)
        store_cache[pack_id] = store
        for event in store.list():
            rid = str(event.get("external_review_id") or event.get("review_id") or "")
            if rid:
                existing_review_ids.add(rid)

    appended = duplicates = invalid = unknown = 0
    touched: set[str] = set()
    errors: list[str] = []

    for index, row in enumerate(rows, start=2):
        external_review_id = row.get("review_id", "").strip()
        language = row.get("language_code", "").strip().casefold()
        spelling = row.get("spelling_status", "").strip().casefold()
        pronunciation = row.get("pronunciation_status", "").strip().casefold()
        familiarity = row.get("place_familiarity", "").strip().casefold()

        if (not external_review_id or language not in lang_to_pack or spelling not in VALID_SPELLING
                or pronunciation not in VALID_PRONUNCIATION or familiarity not in VALID_FAMILIARITY):
            invalid += 1
            errors.append(f"row {index}: invalid status/id/language")
            continue
        if external_review_id in existing_review_ids:
            duplicates += 1
            continue

        pack_id = lang_to_pack[language]
        if pack_id not in candidate_cache:
            candidate_cache[pack_id] = _load_candidates(project_root, pack_id)
        by_id, by_name = candidate_cache[pack_id]

        external_candidate_id = row.get("candidate_id", "").strip()
        canonical = by_id.get(external_candidate_id)
        match_method = "candidate_id"
        if canonical is None:
            matches = by_name.get(_norm(row.get("latin_name", "")), [])
            if len(matches) == 1:
                canonical = matches[0]
                match_method = "language+latin_name"
        if canonical is None:
            unknown += 1
            errors.append(f"row {index}: unknown candidate {external_candidate_id} / {row.get('latin_name','')}")
            continue

        decision, native_name, pron_ok, source_ok = _map_semantics(row)
        metadata = {
            "external_source": "mapvoice-review-railway",
            "external_review_id": external_review_id,
            "external_candidate_id": external_candidate_id,
            "candidate_match_method": match_method,
            "language_code": language,
            "latin_name": row.get("latin_name", "").strip(),
            "suggested_native_name": row.get("suggested_native_name", "").strip(),
            "corrected_native_name": row.get("corrected_native_name", "").strip(),
            "spelling_status": spelling,
            "pronunciation_status": pronunciation,
            "place_familiarity": familiarity,
            "external_created_at": row.get("created_at", "").strip(),
        }
        notes = row.get("notes", "").strip()
        audit_note = "railway_metadata=" + json.dumps(metadata, ensure_ascii=False, sort_keys=True)
        combined_notes = (notes + (" | " if notes else "") + audit_note)

        event = ReviewEvent.create(
            candidate_id=canonical["candidate_id"],
            reviewer_id="railway:" + row.get("reviewer_id", "").strip(),
            stage="independent",
            decision=decision,
            native_name=native_name,
            pronunciation_approved=pron_ok,
            source_approved=source_ok,
            notes=combined_notes,
            review_id=external_review_id,
            created_at=row.get("created_at", "").strip() or None,
            external_review_id=external_review_id,
            external_candidate_id=external_candidate_id,
            external_source="mapvoice-review-railway",
            spelling_status=spelling,
            pronunciation_status=pronunciation,
            place_familiarity=familiarity,
            suggested_native_name=row.get("suggested_native_name", "").strip(),
            corrected_native_name=row.get("corrected_native_name", "").strip(),
        )
        store_cache[pack_id].append(event)
        existing_review_ids.add(external_review_id)
        appended += 1
        touched.add(pack_id)

    return RailwayReviewImportResult(
        rows_seen=len(rows), events_appended=appended, duplicate_review_id=duplicates,
        invalid_rows=invalid, unknown_candidates=unknown,
        packs_touched=tuple(sorted(touched)), errors=tuple(errors),
    )
