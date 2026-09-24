from __future__ import annotations
import csv, json, random
from pathlib import Path
from typing import Iterable
from .entity_schema import EntityRecord

# Backward-compatible alias from v0.1-v0.3.
Entity = EntityRecord
from .pronunciation import build_target

TEMPLATES = [
    "Turn left towards {name}.",
    "Turn right towards {name}.",
    "Continue towards {name}.",
    "In 500m, continue towards {name}.",
    "In 300m, turn left towards {name}.",
    "Proceed straight through {name}.",
    "Keep left towards {name}.",
    "At the next junction, turn right towards {name}.",
]

def read_entities(path: str | Path) -> list[EntityRecord]:
    with open(path, newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        rows = []
        for row in reader:
            rows.append(EntityRecord(
                entity_id=row["entity_id"],
                english_name=row["english_name"],
                kannada_name=row["kannada_name"],
                entity_type=row["entity_type"],
                city=row["city"],
                language=row["language"],
                alternate_spellings=row.get("alternate_spellings", ""),
                morphemes=row.get("morphemes", ""),
                suffix=row.get("suffix", ""),
                verification_status=row.get(
                    "verification_status",
                    "verified" if row.get("verified", "").lower() == "true" else "unverified",
                ),
                pronunciation_verified=row.get("pronunciation_verified", "false"),
                source_name=row.get("source_name", ""),
                source_url=row.get("source_url", ""),
                source_type=row.get("source_type", ""),
                reviewer=row.get("reviewer", ""),
                notes=row.get("notes", ""),
            ))
        return rows

def generate_examples(
    entities: Iterable[EntityRecord],
    verified_only: bool = False,
    pronunciation_verified_only: bool = False,
) -> list[dict]:
    examples = []
    for entity in entities:
        if verified_only and not entity.verified:
            continue
        if pronunciation_verified_only and not entity.pronunciation_is_verified:
            continue

        target = build_target(
            kannada_name=entity.kannada_name,
            fallback_name=entity.english_name,
        )
        for index, template in enumerate(TEMPLATES):
            examples.append({
                "example_id": f"{entity.entity_id}_{index:02d}",
                "entity_id": entity.entity_id,
                "input": {
                    "city": entity.city,
                    "region_language": "Kannada",
                    "navigation_language": "English",
                    "text": template.format(name=entity.english_name),
                },
                "target": {
                    "place_name": entity.english_name,
                    "place_name_kn": entity.kannada_name or None,
                    "entity_type": entity.entity_type,
                    "language_origin": entity.language,
                    "spoken_form": target.spoken_form,
                    "phonetic_form": target.phonetic_form,
                    "pronunciation_representation": target.representation,
                    "pronunciation_form": target.spoken_form,
                },
                "metadata": {
                    "verification_status": entity.verification_status,
                    "pronunciation_verified": entity.pronunciation_is_verified,
                    "suffix": entity.suffix or None,
                    "morphemes": [x.strip() for x in entity.morphemes.split("|") if x.strip()],
                    "alternate_spellings": [
                        x.strip() for x in entity.alternate_spellings.split("|") if x.strip()
                    ],
                    "source_name": entity.source_name or None,
                    "source_url": entity.source_url or None,
                    "source_type": entity.source_type or None,
                },
            })
    return examples

def write_jsonl(records, path: str | Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")

def read_jsonl(path: str | Path) -> list[dict]:
    with open(path, encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]

def split_by_entity(
    examples: list[dict],
    train_ratio: float = 0.70,
    validation_ratio: float = 0.15,
    seed: int = 42,
):
    by_entity = {}
    for example in examples:
        by_entity.setdefault(example["entity_id"], []).append(example)

    ids = sorted(by_entity)
    random.Random(seed).shuffle(ids)
    n = len(ids)
    train_end = int(n * train_ratio)
    validation_end = train_end + int(n * validation_ratio)

    train_ids = set(ids[:train_end])
    validation_ids = set(ids[train_end:validation_end])
    test_ids = set(ids[validation_end:])

    def collect(selected):
        output = []
        for entity_id in sorted(selected):
            output.extend(by_entity[entity_id])
        return output

    return collect(train_ids), collect(validation_ids), collect(test_ids)
