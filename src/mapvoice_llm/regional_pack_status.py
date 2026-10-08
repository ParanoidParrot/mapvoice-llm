from __future__ import annotations

import csv
from pathlib import Path

from .regional_packs import RegionalPackRegistry


def _rows(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open(
        newline="",
        encoding="utf-8",
    ) as handle:
        return list(csv.DictReader(handle))


def regional_pack_status(
    *,
    project_root: Path,
    registry: RegionalPackRegistry,
) -> list[dict]:
    result = []

    for pack in registry.list():
        entity_path = (
            project_root / pack.entity_file
        )
        candidate_path = (
            project_root / pack.candidate_file
            if pack.candidate_file
            else None
        )

        entities = _rows(entity_path)
        candidates = (
            _rows(candidate_path)
            if candidate_path
            else []
        )

        native_candidate_count = sum(
            bool(
                (
                    row.get("native_name")
                    or row.get("kannada_name")
                    or ""
                ).strip()
            )
            for row in candidates
        )

        reviewed_candidates = sum(
            row.get("annotation_status")
            == "reviewed"
            for row in candidates
        )

        manifest = (
            project_root
            / "data"
            / "processed"
            / "packs"
            / pack.pack_id
            / "manifest.json"
        )

        result.append({
            **pack.to_dict(),
            "entity_count": len(entities),
            "candidate_count": len(candidates),
            "candidate_native_names": (
                native_candidate_count
            ),
            "reviewed_candidates": (
                reviewed_candidates
            ),
            "pack_dataset_built": (
                manifest.exists()
            ),
            "manifest_path": (
                str(
                    manifest.relative_to(
                        project_root
                    )
                )
                if manifest.exists()
                else None
            ),
        })

    return result
