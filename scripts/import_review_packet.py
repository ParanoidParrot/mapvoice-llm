from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from mapvoice_llm.review_packet_import import import_review_packet


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pack-id", required=True)
    parser.add_argument("--reviewer-id", required=True)
    parser.add_argument("--packet", required=True)
    parser.add_argument(
        "--stage",
        choices=["independent", "adjudication"],
        default="independent",
    )
    args = parser.parse_args()

    result = import_review_packet(
        project_root=PROJECT_ROOT,
        pack_id=args.pack_id,
        reviewer_id=args.reviewer_id,
        packet_csv=args.packet,
        stage=args.stage,
    )

    print(json.dumps(
        result.to_dict(),
        ensure_ascii=False,
        indent=2,
    ))


if __name__ == "__main__":
    main()
