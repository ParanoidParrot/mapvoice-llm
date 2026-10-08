from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(
    0,
    str(PROJECT_ROOT / "src"),
)

from mapvoice_llm.language_profiles import LanguageProfileRegistry
from mapvoice_llm.language_validation import audit_entities
from mapvoice_llm.pack_context import load_pack_context
from mapvoice_llm.regional_packs import RegionalPackRegistry


def audit_pack(pack_id: str) -> dict:
    context = load_pack_context(
        PROJECT_ROOT,
        pack_id,
    )

    profile = LanguageProfileRegistry(
        PROJECT_ROOT
        / "configs"
        / "language_profiles.json"
    ).get(
        context.pack.region_language_code
    )

    return {
        "pack_id": pack_id,
        **audit_entities(
            context.entity_repository.list(),
            profile,
        ),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pack-id")
    parser.add_argument(
        "--all",
        action="store_true",
    )
    args = parser.parse_args()

    if args.all:
        registry = RegionalPackRegistry(
            PROJECT_ROOT
            / "configs"
            / "regional_packs.json"
        )
        result = {
            "packs": [
                audit_pack(pack.pack_id)
                for pack in registry.list()
            ]
        }
    else:
        if not args.pack_id:
            parser.error(
                "Use --pack-id or --all"
            )
        result = audit_pack(
            args.pack_id
        )

    print(json.dumps(
        result,
        ensure_ascii=False,
        indent=2,
    ))


if __name__ == "__main__":
    main()
