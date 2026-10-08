from __future__ import annotations

import csv
from pathlib import Path

from .regional_entity import RegionalEntity, from_legacy_entity_row


class RegionalEntityRepository:
    def __init__(
        self,
        path: str | Path,
        *,
        language_code: str | None = None,
        native_name_field: str | None = None,
    ):
        self.path = Path(path)
        self.language_code = language_code
        self.native_name_field = native_name_field

    def list(self) -> list[RegionalEntity]:
        with self.path.open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))

        if not rows:
            return []

        if "latin_name" in rows[0] and "native_name" in rows[0]:
            return [
                RegionalEntity(
                    entity_id=row["entity_id"],
                    latin_name=row.get("latin_name", ""),
                    native_name=row.get("native_name", ""),
                    entity_type=row.get("entity_type", ""),
                    city=row.get("city", ""),
                    language=row.get("language", ""),
                    language_code=row.get("language_code") or self.language_code,
                    alternate_spellings=row.get("alternate_spellings", ""),
                    morphemes=row.get("morphemes", ""),
                    suffix=row.get("suffix", ""),
                    verification_status=row.get(
                        "verification_status",
                        "unverified",
                    ),
                    pronunciation_verified=(
                        row.get("pronunciation_verified", "")
                        .strip()
                        .lower()
                        == "true"
                    ),
                    source_name=row.get("source_name", ""),
                    source_url=row.get("source_url", ""),
                    source_type=row.get("source_type", ""),
                    reviewer=row.get("reviewer", ""),
                    notes=row.get("notes", ""),
                )
                for row in rows
            ]

        native_name_field = self.native_name_field or "kannada_name"
        return [
            from_legacy_entity_row(
                row,
                native_name_field=native_name_field,
                language_code=self.language_code,
            )
            for row in rows
        ]

    def by_latin_name(self) -> dict[str, RegionalEntity]:
        return {
            entity.latin_name.casefold(): entity
            for entity in self.list()
            if entity.latin_name
        }
