from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from mapvoice_llm.review_dashboard import review_progress


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pack-id", required=True)
    parser.add_argument(
        "--details",
        action="store_true",
        help="Include candidate-level N-reviewer analysis.",
    )
    args = parser.parse_args()

    report = review_progress(
        PROJECT_ROOT,
        pack_id=args.pack_id,
        include_details=args.details,
    )
    if not report["packs"]:
        raise SystemExit(f"Unknown or unavailable pack: {args.pack_id}")
    print(json.dumps(report["packs"][0], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
