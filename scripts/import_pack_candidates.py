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

from mapvoice_llm.candidate_import import import_candidates
from mapvoice_llm.pack_context import load_pack_context


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--pack-id",
        required=True,
    )
    parser.add_argument(
        "--source-csv",
        required=True,
    )
    args = parser.parse_args()

    context = load_pack_context(
        PROJECT_ROOT,
        args.pack_id,
    )

    result = import_candidates(
        context=context,
        source_csv=args.source_csv,
    )

    print(json.dumps(
        result.to_dict(),
        ensure_ascii=False,
        indent=2,
    ))


if __name__ == "__main__":
    main()
