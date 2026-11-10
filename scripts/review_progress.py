from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from mapvoice_llm.review_dashboard import review_progress


def _print_table(report: dict) -> None:
    headers = [
        "Pack", "Cand", "0", "1", "2", "3+", "Reviews",
        "Disagree", "Adjudicate", "Materialize", "Pron-ready",
    ]
    rows = []
    for pack in report["packs"]:
        buckets = pack["reviewer_buckets"]
        rows.append([
            pack["pack_id"],
            str(pack["candidates"]),
            str(buckets["0"]),
            str(buckets["1"]),
            str(buckets["2"]),
            str(buckets["3+"]),
            str(pack["independent_reviews"]),
            str(pack["disagreements"]),
            str(pack["adjudication_ready"]),
            str(pack["materialization_ready"]),
            str(pack["pronunciation_ready"]),
        ])

    widths = [len(h) for h in headers]
    for row in rows:
        for i, value in enumerate(row):
            widths[i] = max(widths[i], len(value))

    def fmt(row):
        return "  ".join(value.ljust(widths[i]) for i, value in enumerate(row))

    print(fmt(headers))
    print(fmt(["-" * width for width in widths]))
    for row in rows:
        print(fmt(row))

    totals = report["totals"]
    print()
    print(
        "Totals: "
        f"candidates={totals['candidates']} "
        f"reviewed={totals['reviewed_candidates']} "
        f"reviews={totals['independent_reviews']} "
        f"disagreements={totals['disagreements']} "
        f"adjudication_ready={totals['adjudication_ready']} "
        f"materialization_ready={totals['materialization_ready']} "
        f"pronunciation_ready={totals['pronunciation_ready']}"
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Show N-reviewer-aware MapVoice review progress."
    )
    parser.add_argument("--pack-id", help="Limit report to one regional pack.")
    parser.add_argument(
        "--details",
        action="store_true",
        help="Include candidate-level detail in JSON output.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit JSON instead of the default human-readable table.",
    )
    args = parser.parse_args()

    report = review_progress(
        PROJECT_ROOT,
        pack_id=args.pack_id,
        include_details=args.details,
    )
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        _print_table(report)


if __name__ == "__main__":
    main()
