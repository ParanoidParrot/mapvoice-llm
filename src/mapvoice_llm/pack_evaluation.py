from __future__ import annotations

import json
from pathlib import Path

from .pack_dataset import (
    build_pack_examples,
    split_examples_by_entity,
)
from .regional_entity import RegionalEntity
from .regional_packs import RegionalPack


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


def build_pack_evaluation(
    *,
    project_root: str | Path,
    pack: RegionalPack,
    entities: list[RegionalEntity],
    seed: int = 42,
) -> dict:
    project_root = Path(project_root)
    output_dir = (
        project_root
        / "data"
        / "evaluation"
        / "packs"
        / pack.pack_id
    )

    labeled = [
        entity
        for entity in entities
        if entity.latin_name.strip()
        and entity.native_name.strip()
    ]

    examples = build_pack_examples(
        pack=pack,
        entities=labeled,
    )
    splits = split_examples_by_entity(
        examples,
        seed=seed,
    )

    lexicon_known = [
        rows[0]
        for entity_id in sorted({
            row["entity_id"]
            for row in examples
        })
        if (
            rows := [
                row
                for row in examples
                if row["entity_id"] == entity_id
            ]
        )
    ]

    entity_held_out = (
        splits["test"]
    )

    _write_jsonl(
        output_dir
        / "lexicon_known.jsonl",
        lexicon_known,
    )
    _write_jsonl(
        output_dir
        / "entity_held_out.jsonl",
        entity_held_out,
    )

    manifest = {
        "pack_id": pack.pack_id,
        "region_language": (
            pack.region_language
        ),
        "seed": seed,
        "labeled_entities": len(labeled),
        "lexicon_known_examples": (
            len(lexicon_known)
        ),
        "entity_held_out_examples": (
            len(entity_held_out)
        ),
        "status": (
            "ready"
            if labeled
            else "empty-until-labels-reviewed"
        ),
    }

    (output_dir / "manifest.json").write_text(
        json.dumps(
            manifest,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    return {
        **manifest,
        "output_dir": str(
            output_dir.relative_to(
                project_root
            )
        ),
    }
