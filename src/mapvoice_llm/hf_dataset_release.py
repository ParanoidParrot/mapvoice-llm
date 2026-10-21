from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path

from .pack_context import load_pack_context
from .regional_packs import RegionalPackRegistry
from .dataset_snapshot import write_release_snapshot


EXPORT_FIELDS = [
    "record_id", "pack_id", "city", "language", "language_code",
    "latin_name", "native_name", "entity_type", "data_stage",
    "verification_status", "pronunciation_verified", "annotation_status",
    "source_id", "source_record_id", "source_name", "source_url",
    "source_license", "latitude", "longitude", "provenance_status", "notes",
]


def _bool_text(value) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value or "").strip().lower()


def _entity_rows(project_root: Path, pack) -> list[dict]:
    context = load_pack_context(project_root, pack.pack_id)
    result = []
    for entity in context.entity_repository.list():
        stage = "verified" if entity.verification_status == "verified" else "labeled-unverified"
        result.append({
            "record_id": entity.entity_id,
            "pack_id": pack.pack_id,
            "city": pack.city,
            "language": pack.region_language,
            "language_code": pack.region_language_code,
            "latin_name": entity.latin_name,
            "native_name": entity.native_name,
            "entity_type": entity.entity_type,
            "data_stage": stage,
            "verification_status": entity.verification_status,
            "pronunciation_verified": _bool_text(entity.pronunciation_verified),
            "annotation_status": "",
            "source_id": entity.source_type,
            "source_record_id": "",
            "source_name": entity.source_name,
            "source_url": entity.source_url,
            "source_license": "",
            "latitude": "",
            "longitude": "",
            "provenance_status": "",
            "notes": entity.notes,
        })
    return result


def _candidate_rows(project_root: Path, pack) -> list[dict]:
    context = load_pack_context(project_root, pack.pack_id)
    if context.candidate_csv is None or not context.candidate_csv.exists():
        return []

    with context.candidate_csv.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))

    result = []
    for row in rows:
        result.append({
            "record_id": row.get("candidate_id", ""),
            "pack_id": pack.pack_id,
            "city": pack.city,
            "language": pack.region_language,
            "language_code": pack.region_language_code,
            "latin_name": row.get("latin_name") or row.get("english_name") or "",
            "native_name": row.get("native_name") or row.get("kannada_name") or "",
            "entity_type": row.get("entity_type", ""),
            "data_stage": "candidate",
            "verification_status": "unverified",
            "pronunciation_verified": "false",
            "annotation_status": row.get("annotation_status", ""),
            "source_id": row.get("source_id", ""),
            "source_record_id": row.get("source_record_id", ""),
            "source_name": row.get("source_name", ""),
            "source_url": row.get("source_url", ""),
            "source_license": row.get("source_license", ""),
            "latitude": row.get("latitude", ""),
            "longitude": row.get("longitude", ""),
            "provenance_status": row.get("provenance_status", ""),
            "notes": row.get("notes", ""),
        })
    return result


def _reviewed_rows(project_root: Path, pack) -> list[dict]:
    path = project_root / "data" / "reviewed" / pack.pack_id / "entities.csv"
    if not path.exists():
        return []

    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))

    result = []
    for row in rows:
        result.append({
            "record_id": row.get("entity_id", ""),
            "pack_id": pack.pack_id,
            "city": pack.city,
            "language": pack.region_language,
            "language_code": pack.region_language_code,
            "latin_name": row.get("latin_name") or row.get("english_name") or "",
            "native_name": row.get("native_name") or row.get("kannada_name") or "",
            "entity_type": row.get("entity_type", ""),
            "data_stage": "reviewed",
            "verification_status": row.get("verification_status", "verified"),
            "pronunciation_verified": _bool_text(row.get("pronunciation_verified")),
            "annotation_status": "reviewed",
            "source_id": row.get("source_type", ""),
            "source_record_id": "",
            "source_name": row.get("source_name", ""),
            "source_url": row.get("source_url", ""),
            "source_license": "",
            "latitude": "",
            "longitude": "",
            "provenance_status": "reviewed",
            "notes": row.get("notes", ""),
        })
    return result


def _dedupe_preview(rows: list[dict]) -> list[dict]:
    priority = {"verified": 3, "labeled-unverified": 2, "candidate": 1}
    chosen = {}
    for row in rows:
        key = (row["pack_id"], row["latin_name"].strip().casefold())
        current = chosen.get(key)
        if current is None or priority.get(row["data_stage"], 0) > priority.get(current["data_stage"], 0):
            chosen[key] = row
    return sorted(chosen.values(), key=lambda x: (x["pack_id"], x["latin_name"].casefold()))


def _write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=EXPORT_FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in EXPORT_FIELDS})


def _release_license(rows: list[dict]) -> tuple[str, str]:
    licenses = {
        row.get("source_license", "").strip()
        for row in rows
        if row.get("source_license", "").strip()
    }

    if not licenses:
        return (
            "cc-by-4.0",
            "The MapVoice-authored preview/annotation layer is released under CC BY 4.0. "
            "Future upstream-derived rows retain their row-level source license."
        )

    if licenses == {"ODbL-1.0"}:
        return (
            "odbl",
            "This release contains OSM-derived database content; ODbL obligations and OpenStreetMap attribution apply."
        )

    return (
        "other",
        "This release contains mixed upstream licenses. See source_license on each row and LICENSE_DATA.md."
    )


def build_hf_release(
    *,
    project_root: str | Path,
    release_name: str = "mapvoice-india-toponyms-preview",
    version: str = "0.1.0",
) -> dict:
    project_root = Path(project_root)
    registry = RegionalPackRegistry(
        project_root / "configs" / "regional_packs.json"
    )

    preview_source = []
    reviewed = []

    for pack in registry.list():
        preview_source.extend(_candidate_rows(project_root, pack))
        preview_source.extend(_entity_rows(project_root, pack))
        reviewed.extend(_reviewed_rows(project_root, pack))

    preview = _dedupe_preview(preview_source)

    out = (
        project_root
        / "outputs"
        / "hf_datasets"
        / f"{release_name}-v{version}"
    )

    if out.exists():
        import shutil
        shutil.rmtree(out)

    (out / "data").mkdir(parents=True, exist_ok=True)

    _write_csv(out / "data" / "preview.csv", preview)
    _write_csv(out / "data" / "reviewed.csv", reviewed)

    combined = preview + reviewed
    hf_license, license_note = _release_license(combined)

    counts_by_pack = {}
    for pack_id in sorted({row["pack_id"] for row in combined}):
        rows = [row for row in combined if row["pack_id"] == pack_id]
        counts_by_pack[pack_id] = {
            "preview": sum(row["data_stage"] != "reviewed" for row in rows),
            "reviewed": sum(row["data_stage"] == "reviewed" for row in rows),
            "with_native_name": sum(bool(row["native_name"].strip()) for row in rows),
            "pronunciation_verified": sum(row["pronunciation_verified"] == "true" for row in rows),
        }

    reviewed_pack_ids = {row["pack_id"] for row in reviewed}
    pronunciation_verified = [
        row for row in reviewed
        if row["pronunciation_verified"] == "true"
    ]

    manifest = {
        "dataset_name": release_name,
        "version": version,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "release_tier": "preview",
        "languages": ["kn", "ta", "te", "mr", "ml"],
        "cities": ["Bengaluru", "Chennai", "Hyderabad", "Mumbai", "Kochi"],
        "preview_rows": len(preview),
        "reviewed_rows": len(reviewed),
        "counts_by_pack": counts_by_pack,
        "hf_license": hf_license,
        "license_note": license_note,
        "publication_guardrails": {
            "early_preview_dataset": len(preview) > 0,
            "reviewed_dataset": len(reviewed) > 0,
            "reviewed_multilingual_dataset": len(reviewed_pack_ids) >= 2,
            "pronunciation_verified_dataset": len(pronunciation_verified) >= 20,
            "training_ready_multilingual_dataset": False,
        },
    }

    (out / "release_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    card = f"""---
language:
- kn
- ta
- te
- mr
- ml
- en
license: {hf_license}
pretty_name: "MapVoice Indian Navigation Toponyms — Preview"
tags:
- indian-languages
- navigation
- toponyms
- place-names
- multilingual
- transliteration
- pronunciation
- geospatial
configs:
- config_name: preview
  data_files:
  - split: train
    path: data/preview.csv
- config_name: reviewed
  data_files:
  - split: train
    path: data/reviewed.csv
---

# MapVoice Indian Navigation Toponyms — Preview

**Version:** {version}

MapVoice is a city-specific Indian navigation/place-name data project covering Bengaluru/Kannada, Chennai/Tamil, Hyderabad/Telugu, Mumbai/Marathi and Kochi/Malayalam.

## Maturity

This repository deliberately separates **candidate**, **labeled-but-unverified**, and **reviewed** records.

- `preview` is for exploration, review tooling and early experiments.
- `reviewed` contains only rows materialized through the MapVoice independent-review/adjudication workflow.
- A native-script value does **not** imply pronunciation verification.
- This release is not a production-grade or fully pronunciation-verified corpus.

## Current counts

```json
{json.dumps(counts_by_pack, ensure_ascii=False, indent=2)}
```

## Provenance and licensing

{license_note}

Rows derived from upstream data retain source identity/license in row metadata.

## Review methodology

Two independent reviews are required for verification; disagreements require adjudication. Pronunciation approval is recorded separately from spelling/source approval.

## Limitations

Coverage is incomplete and uneven. Candidate rows may lack native-script forms or authoritative provenance. Unverified rows are not gold labels.

## Related work

Indian locality-pronunciation benchmarks already exist, including the Koel Benchmark Suite. MapVoice focuses on city-specific navigation adaptation, provenance/review lifecycle, held-out evaluation and a planned regional adapter family.

## Citation

A formal citation will be added when the dataset reaches a stable reviewed release.
"""
    (out / "README.md").write_text(card, encoding="utf-8")

    (out / "LICENSE_DATA.md").write_text(
        f"""# Data licensing

{license_note}

MapVoice-authored preview/annotation content is offered under CC BY 4.0 unless a row records a different upstream source license.

Rows marked `source_license=ODbL-1.0` retain OpenStreetMap/Open Database License obligations and require attribution to © OpenStreetMap contributors.

Other upstream rows retain the license recorded in `source_license`.
""",
        encoding="utf-8",
    )

    write_release_snapshot(
        release_dir=out,
    )

    return {
        **manifest,
        "output_dir": str(out.relative_to(project_root)),
    }
