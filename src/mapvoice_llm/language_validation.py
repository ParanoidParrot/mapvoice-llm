from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Iterable

from .language_profiles import LanguageProfile
from .regional_entity import RegionalEntity


@dataclass(frozen=True)
class LabelAudit:
    entity_id: str
    latin_name: str
    native_name: str
    ok: bool
    native_script_fraction: float
    issues: list[str]

    def to_dict(self) -> dict:
        return asdict(self)


def _letters(text: str) -> list[str]:
    return [char for char in text if char.isalpha()]


def native_script_fraction(
    text: str,
    profile: LanguageProfile,
) -> float:
    letters = _letters(text)
    if not letters:
        return 0.0

    in_script = sum(
        profile.codepoint_in_script(ord(char))
        for char in letters
    )
    return in_script / len(letters)


def audit_entity_label(
    entity: RegionalEntity,
    profile: LanguageProfile,
    *,
    minimum_script_fraction: float = 0.60,
) -> LabelAudit:
    issues: list[str] = []
    native_name = (entity.native_name or "").strip()

    if not native_name:
        issues.append("missing_native_name")
        fraction = 0.0
    else:
        fraction = native_script_fraction(
            native_name,
            profile,
        )
        if fraction < minimum_script_fraction:
            issues.append(
                "native_name_script_mismatch"
            )

    if not entity.latin_name.strip():
        issues.append("missing_latin_name")

    if entity.pronunciation_verified and not native_name:
        issues.append(
            "pronunciation_verified_without_native_name"
        )

    if (
        entity.verification_status == "verified"
        and not entity.source_name.strip()
    ):
        issues.append(
            "verified_without_source"
        )

    return LabelAudit(
        entity_id=entity.entity_id,
        latin_name=entity.latin_name,
        native_name=entity.native_name,
        ok=not issues,
        native_script_fraction=round(fraction, 4),
        issues=issues,
    )


def audit_entities(
    entities: Iterable[RegionalEntity],
    profile: LanguageProfile,
    *,
    minimum_script_fraction: float = 0.60,
) -> dict:
    audits = [
        audit_entity_label(
            entity,
            profile,
            minimum_script_fraction=minimum_script_fraction,
        )
        for entity in entities
    ]

    issue_counts: dict[str, int] = {}
    for audit in audits:
        for issue in audit.issues:
            issue_counts[issue] = (
                issue_counts.get(issue, 0) + 1
            )

    return {
        "language_code": profile.language_code,
        "language": profile.language,
        "script_name": profile.script_name,
        "entities": len(audits),
        "ok": sum(item.ok for item in audits),
        "with_issues": sum(not item.ok for item in audits),
        "issue_counts": issue_counts,
        "rows": [
            item.to_dict()
            for item in audits
        ],
    }
