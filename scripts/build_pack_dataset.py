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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pack-id")
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
    )
    parser.add_argument(
        "--policy",
        choices=sorted(POLICIES),
        default="labeled",
    )
    args = parser.parse_args()

    context = load_pack_context(
        PROJECT_ROOT,
        args.pack_id,
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

    print(json.dumps(
        result.to_dict(),
        ensure_ascii=False,
        indent=2,
    ))


if __name__ == "__main__":
    main()
