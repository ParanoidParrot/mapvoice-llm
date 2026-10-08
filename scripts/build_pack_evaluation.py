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

from mapvoice_llm.pack_context import load_pack_context
from mapvoice_llm.pack_evaluation import build_pack_evaluation


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--pack-id",
        required=True,
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
    )
    args = parser.parse_args()

    context = load_pack_context(
        PROJECT_ROOT,
        args.pack_id,
    )

    result = build_pack_evaluation(
        project_root=PROJECT_ROOT,
        pack=context.pack,
        entities=(
            context.entity_repository.list()
        ),
        seed=args.seed,
    )

    print(json.dumps(
        result,
        ensure_ascii=False,
        indent=2,
    ))


if __name__ == "__main__":
    main()
