from __future__ import annotations

from pathlib import Path

from .entity_repository import RegionalEntityRepository
from .normalization import normalize_navigation_text
from .pronunciation import build_target
from .schemas import PronunciationResult


class RuleBaseline:
    def __init__(self, entity_csv: str | Path):
        self.repository = RegionalEntityRepository(entity_csv)
        self.entities = self.repository.list()

    def predict(self, text: str) -> PronunciationResult:
        normalized = normalize_navigation_text(text)

        detected = None
        for entity in sorted(
            self.entities,
            key=lambda item: len(item.latin_name),
            reverse=True,
        ):
            candidates = [entity.latin_name]
            candidates.extend(
                alias.strip()
                for alias in (
                    entity.alternate_spellings or ""
                ).split("|")
                if alias.strip()
            )

            if any(
                candidate.casefold()
                in text.casefold()
                for candidate in candidates
            ):
                detected = entity
                break

        pronunciation = build_target(
            native_name=(
                detected.native_name
                if detected
                else None
            ),
            fallback_name=(
                detected.latin_name
                if detected
                else None
            ),
        )

        return PronunciationResult(
            original_text=text,
            normalized_instruction=normalized,
            detected_entity=(
                detected.latin_name
                if detected
                else None
            ),
            entity_native=(
                detected.native_name
                if detected
                else None
            ),
            # Legacy UI/API alias retained.
            entity_kannada=(
                detected.native_name
                if detected
                else None
            ),
            entity_type=(
                detected.entity_type
                if detected
                else None
            ),
            spoken_form=pronunciation.spoken_form,
            phonetic_form=pronunciation.phonetic_form,
            pronunciation_representation=(
                pronunciation.representation
            ),
            pronunciation_form=pronunciation.spoken_form,
            source="rule-baseline",
        )
