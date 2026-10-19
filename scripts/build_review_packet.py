from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from mapvoice_llm.pack_context import load_pack_context
from mapvoice_llm.review_packet import build_review_packet


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pack-id", required=True)
    parser.add_argument("--output")
    args = parser.parse_args()

    context = load_pack_context(PROJECT_ROOT, args.pack_id)
    if context.candidate_csv is None:
        raise SystemExit("Pack has no candidate file")

    output = (
        Path(args.output)
        if args.output
        else (
            PROJECT_ROOT
            / "data"
            / "review_packets"
            / f"{args.pack_id}.csv"
        )
    )

    result = build_review_packet(
        project_root=PROJECT_ROOT,
        pack_id=args.pack_id,
        candidate_csv=context.candidate_csv,
        output=output,
    )

    print(json.dumps(
        result,
        ensure_ascii=False,
        indent=2,
    ))


if __name__ == "__main__":
    main()
