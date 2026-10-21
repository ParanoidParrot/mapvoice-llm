from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from mapvoice_llm.candidate_conflicts import audit_candidate_conflicts
from mapvoice_llm.pack_context import load_pack_context


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pack-id", required=True)
    parser.add_argument("--output")
    args = parser.parse_args()

    context = load_pack_context(
        PROJECT_ROOT,
        args.pack_id,
    )

    result = audit_candidate_conflicts(
        context.candidate_csv
    )

    if args.output:
        Path(args.output).write_text(
            json.dumps(
                result,
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

    print(json.dumps(
        result,
        ensure_ascii=False,
        indent=2,
    ))


if __name__ == "__main__":
    main()
