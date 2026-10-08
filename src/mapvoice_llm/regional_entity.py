from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any


@dataclass
class RegionalEntity:
    entity_id: str
    latin_name: str
    native_name: str
    entity_type: str
    city: str
    language: str
    language_code: str | None = None
    alternate_spellings: str = ""
    morphemes: str = ""
    suffix: str = ""
    verification_status: str = "unverified"
    pronunciation_verified: bool = False
    source_name: str = ""
    source_url: str = ""
    source_type: str = ""
    reviewer: str = ""
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def from_legacy_entity_row(
    row: dict[str, str],
    *,
    native_name_field: str = "kannada_name",
    language_code: str | None = None,
) -> RegionalEntity:
    return RegionalEntity(
        entity_id=row["entity_id"],
        latin_name=row.get("english_name", ""),
        native_name=row.get(native_name_field, ""),
        entity_type=row.get("entity_type", ""),
        city=row.get("city", ""),
        language=row.get("language", ""),
        language_code=language_code,
        alternate_spellings=row.get("alternate_spellings", ""),
        morphemes=row.get("morphemes", ""),
        suffix=row.get("suffix", ""),
        verification_status=row.get("verification_status", "unverified"),
        pronunciation_verified=(
            row.get("pronunciation_verified", "").strip().lower() == "true"
        ),
        source_name=row.get("source_name", ""),
        source_url=row.get("source_url", ""),
        source_type=row.get("source_type", ""),
        reviewer=row.get("reviewer", ""),
        notes=row.get("notes", ""),
    )
