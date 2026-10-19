from __future__ import annotations

import json
import random
from pathlib import Path

from .entity_repository import RegionalEntityRepository
from .pack_dataset import build_pack_examples
from .pilot_profiles import PilotProfile


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


def pilot_status(
    *,
    project_root: str | Path,
    pack_id: str,
    profile: PilotProfile,
) -> dict:
    project_root = Path(
        project_root
    )

    reviewed_file = (
        project_root
        / "data"
        / "reviewed"
        / pack_id
        / "entities.csv"
    )

    if not reviewed_file.exists():
        return {
            "pack_id": pack_id,
            "ready": False,
            "verified_entities": 0,
            "minimum_verified_entities": (
                profile.minimum_verified_entities
            ),
            "reason": (
                "reviewed dataset has not "
                "been materialized"
            ),
        }

    entities = (
        RegionalEntityRepository(
            reviewed_file
        ).list()
    )

    verified = [
        entity
        for entity in entities
        if (
            entity.verification_status
            == "verified"
            and entity.native_name.strip()
            and entity.source_name.strip()
        )
    ]

    return {
        "pack_id": pack_id,
        "ready": (
            len(verified)
            >= profile.minimum_verified_entities
        ),
        "verified_entities": (
            len(verified)
        ),
        "minimum_verified_entities": (
            profile.minimum_verified_entities
        ),
        "reviewed_file": str(
            reviewed_file.relative_to(
                project_root
            )
        ),
    }


def build_pilot(
    *,
    project_root: str | Path,
    pack,
    profile: PilotProfile,
    seed: int = 20261018,
) -> dict:
    project_root = Path(
        project_root
    )

    status = pilot_status(
        project_root=project_root,
        pack_id=pack.pack_id,
        profile=profile,
    )

    if not status["ready"]:
        return {
            **status,
            "built": False,
        }

    reviewed_file = (
        project_root
        / "data"
        / "reviewed"
        / pack.pack_id
        / "entities.csv"
    )

    entities = [
        entity
        for entity in (
            RegionalEntityRepository(
                reviewed_file
            ).list()
        )
        if (
            entity.verification_status
            == "verified"
            and entity.native_name.strip()
            and entity.source_name.strip()
        )
    ]

    rng = random.Random(
        seed
    )
    rng.shuffle(
        entities
    )

    needed = (
        profile.train_entities
        + profile.validation_entities
        + profile.test_entities
    )

    entities = (
        entities[:needed]
    )

    train_entities = (
        entities[
            :profile.train_entities
        ]
    )

    validation_entities = (
        entities[
            profile.train_entities:
            profile.train_entities
            + profile.validation_entities
        ]
    )

    test_entities = (
        entities[
            profile.train_entities
            + profile.validation_entities:
            needed
        ]
    )

    split_entities = {
        "train": (
            train_entities
        ),
        "validation": (
            validation_entities
        ),
        "test": (
            test_entities
        ),
    }

    output_dir = (
        project_root
        / "data"
        / "pilots"
        / pack.pack_id
    )

    split_examples = {}

    for (
        split,
        split_rows,
    ) in split_entities.items():
        examples = (
            build_pack_examples(
                pack=pack,
                entities=split_rows,
            )
        )

        _write_jsonl(
            output_dir
            / f"{split}.jsonl",
            examples,
        )

        split_examples[
            split
        ] = len(
            examples
        )

    manifest = {
        "pilot_format_version": 1,
        "pack_id": (
            pack.pack_id
        ),
        "seed": seed,
        "verified_entities": (
            len(entities)
        ),
        "entity_split": {
            "train": (
                len(
                    train_entities
                )
            ),
            "validation": (
                len(
                    validation_entities
                )
            ),
            "test": (
                len(
                    test_entities
                )
            ),
        },
        "example_split": (
            split_examples
        ),
        "source_reviewed_file": str(
            reviewed_file.relative_to(
                project_root
            )
        ),
        "purpose": (
            "Small feasibility pilot only. "
            "Not a production or publishable "
            "regional adapter corpus."
        ),
    }

    (
        output_dir
        / "manifest.json"
    ).write_text(
        json.dumps(
            manifest,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    return {
        **status,
        "built": True,
        "output_dir": str(
            output_dir.relative_to(
                project_root
            )
        ),
        "manifest": (
            manifest
        ),
    }
