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

from mapvoice_llm.data_quality import POLICIES
from mapvoice_llm.pack_context import load_pack_context
from mapvoice_llm.pack_dataset import build_pack_dataset
from mapvoice_llm.regional_packs import RegionalPackRegistry


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--policy",
        choices=sorted(POLICIES),
        default="labeled",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
    )
    args = parser.parse_args()

    registry = RegionalPackRegistry(
        PROJECT_ROOT
        / "configs"
        / "regional_packs.json"
    )

    results = []

    for pack in registry.list():
        # Hindi is intentionally absent from the registry/project.
        context = load_pack_context(
            PROJECT_ROOT,
            pack.pack_id,
        )

        result = build_pack_dataset(
            project_root=PROJECT_ROOT,
            pack=context.pack,
            entity_repository=(
                context.entity_repository
            ),
            seed=args.seed,
            policy_id=args.policy,
        )
        results.append(
            result.to_dict()
        )

    print(json.dumps({
        "policy": args.policy,
        "packs": results,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
