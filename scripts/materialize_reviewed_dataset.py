from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from mapvoice_llm.pack_context import load_pack_context
from mapvoice_llm.review_materializer import materialize_reviewed_entities


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--pack-id",
        required=True,
    )
    args = parser.parse_args()

    context = load_pack_context(
        PROJECT_ROOT,
        args.pack_id,
    )

    if context.candidate_csv is None:
        raise SystemExit(
            "Pack has no candidate file"
        )

    result = (
        materialize_reviewed_entities(
            project_root=PROJECT_ROOT,
            pack=context.pack,
            candidate_csv=(
                context.candidate_csv
            ),
        )
    )

    print(json.dumps(
        result,
        ensure_ascii=False,
        indent=2,
    ))


if __name__ == "__main__":
    main()
