from __future__ import annotations

import hashlib
import json
import random
from dataclasses import dataclass
from pathlib import Path

from .data_quality import filter_entities, get_policy
from .entity_repository import RegionalEntityRepository
from .language_profiles import LanguageProfileRegistry
from .language_validation import audit_entities
from .regional_entity import RegionalEntity
from .regional_packs import RegionalPack


NAVIGATION_TEMPLATES = [
    "Continue towards {name}.",
    "Turn left towards {name}.",
    "Turn right towards {name}.",
    "Keep left for {name}.",
    "Keep right for {name}.",
    "In 300 meters, continue towards {name}.",
    "Take the next exit towards {name}.",
    "You are approaching {name}.",
]


@dataclass(frozen=True)
class PackDatasetBuildResult:
    pack_id: str
    policy_id: str
    source_entities: int
    included_entities: int
    total_examples: int
    split_entities: dict[str, int]
    split_examples: dict[str, int]
    output_dir: str
    manifest_file: str

    def to_dict(self) -> dict:
        return self.__dict__.copy()


def _example_id(
    pack_id: str,
    entity_id: str,
    index: int,
) -> str:
    digest = hashlib.sha1(
        f"{pack_id}:{entity_id}:{index}".encode(
            "utf-8"
        )
    ).hexdigest()[:10]
    return f"{pack_id}_{digest}"


def build_pack_examples(
    *,
    pack: RegionalPack,
    entities: list[RegionalEntity],
) -> list[dict]:
    rows = []

    for entity in entities:
        for index, template in enumerate(
            NAVIGATION_TEMPLATES
        ):
            rows.append({
                "example_id": _example_id(
                    pack.pack_id,
                    entity.entity_id,
                    index,
                ),
                "entity_id": entity.entity_id,
                "pack_id": pack.pack_id,
                "input": {
                    "city": pack.city,
                    "region_language": (
                        pack.region_language
                    ),
                    "region_language_code": (
                        pack.region_language_code
                    ),
                    "navigation_language": "English",
                    "text": template.format(
                        name=entity.latin_name
                    ),
                },
                "target": {
                    "place_name": entity.latin_name,
                    "place_name_native": (
                        entity.native_name
                    ),
                    # Legacy compatibility for older evaluators.
                    "place_name_kn": (
                        entity.native_name
                    ),
                    "entity_type": entity.entity_type,
                    "language_origin": entity.language,
                    "spoken_form": entity.native_name,
                    "phonetic_form": None,
                    "pronunciation_representation": (
                        "native-script"
                    ),
                },
                "metadata": {
                    "verification_status": (
                        entity.verification_status
                    ),
                    "pronunciation_verified": (
                        entity.pronunciation_verified
                    ),
                    "source_name": (
                        entity.source_name
                    ),
                    "source_url": (
                        entity.source_url
                    ),
                    "suffix": entity.suffix,
                },
            })

    return rows


def split_examples_by_entity(
    examples: list[dict],
    *,
    seed: int = 42,
    train_ratio: float = 0.70,
    validation_ratio: float = 0.15,
) -> dict[str, list[dict]]:
    by_entity: dict[str, list[dict]] = {}

    for row in examples:
        by_entity.setdefault(
            row["entity_id"],
            [],
        ).append(row)

    entity_ids = sorted(by_entity)
    random.Random(seed).shuffle(entity_ids)
    total = len(entity_ids)

    if total == 0:
        return {
            "train": [],
            "validation": [],
            "test": [],
        }

    if total == 1:
        train_ids = set(entity_ids)
        validation_ids = set()
        test_ids = set()
    elif total == 2:
        train_ids = {entity_ids[0]}
        validation_ids = set()
        test_ids = {entity_ids[1]}
    else:
        train_n = round(total * train_ratio)
        validation_n = round(
            total * validation_ratio
        )

        train_n = max(
            1,
            min(train_n, total - 2),
        )
        validation_n = max(
            1,
            min(
                validation_n,
                total - train_n - 1,
            ),
        )

        train_ids = set(
            entity_ids[:train_n]
        )
        validation_ids = set(
            entity_ids[
                train_n:
                train_n + validation_n
            ]
        )
        test_ids = set(
            entity_ids[
                train_n + validation_n:
            ]
        )

    split_ids = {
        "train": train_ids,
        "validation": validation_ids,
        "test": test_ids,
    }

    return {
        split: [
            row
            for row in examples
            if row["entity_id"] in ids
        ]
        for split, ids in split_ids.items()
    }


def _write_jsonl(
    path: Path,
    rows: list[dict],
) -> None:
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with path.open(
        "w",
        encoding="utf-8",
    ) as handle:
        for row in rows:
            handle.write(
                json.dumps(
                    row,
                    ensure_ascii=False,
                )
                + "\n"
            )


def build_pack_dataset(
    *,
    project_root: str | Path,
    pack: RegionalPack,
    entity_repository: RegionalEntityRepository,
    seed: int = 42,
    policy_id: str = "labeled",
) -> PackDatasetBuildResult:
    project_root = Path(project_root)
    output_dir = (
        project_root
        / "data"
        / "processed"
        / "packs"
        / pack.pack_id
        / policy_id
    )

    entities = entity_repository.list()
    policy = get_policy(policy_id)

    included_entities, quality = filter_entities(
        entities,
        policy,
    )

    language_profile_file = (
        project_root
        / "configs"
        / "language_profiles.json"
    )

    if language_profile_file.exists():
        language_registry = LanguageProfileRegistry(
            language_profile_file
        )
        language_profile = language_registry.get(
            pack.region_language_code
        )
        label_audit = audit_entities(
            included_entities,
            language_profile,
        )
    else:
        # Library callers/tests can build a dataset in an isolated project root
        # without copying repository-level config. The real repo always ships
        # language_profiles.json and therefore always performs the script audit.
        label_audit = {
            "language_code": pack.region_language_code,
            "language": pack.region_language,
            "script_name": None,
            "entities": len(included_entities),
            "ok": None,
            "with_issues": None,
            "issue_counts": {},
            "status": "skipped-language-profile-config-missing",
            "rows": [],
        }

    examples = build_pack_examples(
        pack=pack,
        entities=included_entities,
    )
    splits = split_examples_by_entity(
        examples,
        seed=seed,
    )

    for split, rows in splits.items():
        _write_jsonl(
            output_dir / f"{split}.jsonl",
            rows,
        )

    _write_jsonl(
        output_dir / "all.jsonl",
        examples,
    )

    # Backward compatibility for the first Bengaluru workflow:
    # the default "labeled" corpus is also mirrored at the historical
    # data/processed/packs/<pack-id>/ location.
    compatibility_dir = (
        project_root
        / "data"
        / "processed"
        / "packs"
        / pack.pack_id
    )
    if policy_id == "labeled":
        for split, rows in splits.items():
            _write_jsonl(
                compatibility_dir / f"{split}.jsonl",
                rows,
            )
        _write_jsonl(
            compatibility_dir / "all.jsonl",
            examples,
        )

    split_entities = {
        split: len({
            row["entity_id"]
            for row in rows
        })
        for split, rows in splits.items()
    }
    split_examples = {
        split: len(rows)
        for split, rows in splits.items()
    }

    manifest = {
        "dataset_format_version": 2,
        "pack_id": pack.pack_id,
        "city": pack.city,
        "region_language": (
            pack.region_language
        ),
        "region_language_code": (
            pack.region_language_code
        ),
        "source_entity_file": (
            pack.entity_file
        ),
        "seed": seed,
        "split_strategy": "entity-level",
        "dataset_policy": quality["policy"],
        "source_entities": len(entities),
        "included_entities": (
            len(included_entities)
        ),
        "excluded_entities": (
            quality["excluded_entities"]
        ),
        "exclusion_reason_counts": (
            quality[
                "exclusion_reason_counts"
            ]
        ),
        "total_examples": len(examples),
        "split_entities": split_entities,
        "split_examples": split_examples,
        "label_audit": {
            key: value
            for key, value in label_audit.items()
            if key != "rows"
        },
    }

    manifest_file = (
        output_dir / "manifest.json"
    )
    manifest_file.write_text(
        json.dumps(
            manifest,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    if policy_id == "labeled":
        (compatibility_dir / "manifest.json").write_text(
            json.dumps(
                manifest,
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

    quality_file = (
        output_dir
        / "excluded_entities.json"
    )
    quality_file.write_text(
        json.dumps(
            quality["excluded"],
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    audit_file = (
        output_dir
        / "label_audit.json"
    )
    audit_file.write_text(
        json.dumps(
            label_audit,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    return PackDatasetBuildResult(
        pack_id=pack.pack_id,
        policy_id=policy_id,
        source_entities=len(entities),
        included_entities=(
            len(included_entities)
        ),
        total_examples=len(examples),
        split_entities=split_entities,
        split_examples=split_examples,
        output_dir=str(
            output_dir.relative_to(
                project_root
            )
        ),
        manifest_file=str(
            manifest_file.relative_to(
                project_root
            )
        ),
    )
