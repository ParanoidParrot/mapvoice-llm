from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from mapvoice_llm.review_models import ReviewEvent
from mapvoice_llm.review_store import ReviewStore


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pack-id", required=True)
    parser.add_argument("--candidate-id", required=True)
    parser.add_argument("--reviewer-id", required=True)
    parser.add_argument(
        "--stage",
        choices=[
            "independent",
            "adjudication",
        ],
        default="independent",
    )
    parser.add_argument(
        "--decision",
        choices=[
            "approve",
            "reject",
            "needs-correction",
        ],
        required=True,
    )
    parser.add_argument(
        "--native-name",
        default="",
    )
    parser.add_argument(
        "--source-approved",
        action="store_true",
    )
    parser.add_argument(
        "--pronunciation-approved",
        action="store_true",
    )
    parser.add_argument(
        "--notes",
        default="",
    )
    args = parser.parse_args()

    event = ReviewEvent.create(
        candidate_id=args.candidate_id,
        reviewer_id=args.reviewer_id,
        stage=args.stage,
        decision=args.decision,
        native_name=args.native_name,
        source_approved=(
            args.source_approved
        ),
        pronunciation_approved=(
            args.pronunciation_approved
        ),
        notes=args.notes,
    )

    ReviewStore(
        PROJECT_ROOT,
        args.pack_id,
    ).append(event)

    print(json.dumps(
        event.to_dict(),
        ensure_ascii=False,
        indent=2,
    ))


if __name__ == "__main__":
    main()
