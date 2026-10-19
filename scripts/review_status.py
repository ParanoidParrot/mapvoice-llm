from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from mapvoice_llm.pack_context import load_pack_context
from mapvoice_llm.review_consensus import resolve_candidate_reviews
from mapvoice_llm.review_store import ReviewStore


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

    with context.candidate_csv.open(
        newline="",
        encoding="utf-8",
    ) as handle:
        candidates = list(
            csv.DictReader(
                handle
            )
        )

    store = ReviewStore(
        PROJECT_ROOT,
        args.pack_id,
    )

    by_candidate = {}
    events = store.list()

    for event in events:
        by_candidate.setdefault(
            event["candidate_id"],
            [],
        ).append(event)

    statuses = Counter()

    for candidate in candidates:
        consensus = resolve_candidate_reviews(
            by_candidate.get(
                candidate["candidate_id"],
                [],
            )
        )
        statuses[
            consensus["status"]
        ] += 1

    print(json.dumps({
        "pack_id": args.pack_id,
        "candidates": (
            len(candidates)
        ),
        "review_events": (
            len(events)
        ),
        "statuses": (
            dict(statuses)
        ),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
