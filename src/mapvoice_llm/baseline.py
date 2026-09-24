from pathlib import Path
import csv

from .normalization import normalize_navigation_text
from .pronunciation import build_target
from .schemas import PronunciationResult


class RuleBaseline:
    def __init__(self, entity_csv: str | Path):
        self.entities: list[dict] = []
        with open(entity_csv, newline="", encoding="utf-8") as handle:
            self.entities = list(csv.DictReader(handle))

    def predict(self, text: str) -> PronunciationResult:
        normalized = normalize_navigation_text(text)

        detected = None
        for entity in sorted(
            self.entities,
            key=lambda row: len(row["english_name"]),
            reverse=True,
        ):
            candidates = [entity["english_name"]]
            candidates.extend(
                alias.strip()
                for alias in (entity.get("alternate_spellings") or "").split("|")
                if alias.strip()
            )

            if any(candidate.lower() in text.lower() for candidate in candidates):
                detected = entity
                break

        pronunciation = build_target(
            kannada_name=detected["kannada_name"] if detected else None,
            fallback_name=detected["english_name"] if detected else None,
        )

        return PronunciationResult(
            original_text=text,
            normalized_instruction=normalized,
            detected_entity=detected["english_name"] if detected else None,
            entity_kannada=detected["kannada_name"] if detected else None,
            entity_type=detected["entity_type"] if detected else None,
            spoken_form=pronunciation.spoken_form,
            phonetic_form=pronunciation.phonetic_form,
            pronunciation_representation=pronunciation.representation,
            pronunciation_form=pronunciation.spoken_form,
            source="rule-baseline",
        )
