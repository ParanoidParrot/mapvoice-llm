from __future__ import annotations
import argparse
import csv
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from mapvoice_llm.pack_context import load_pack_context
from mapvoice_llm.review_queue import build_review_queue

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pack-id", required=True)
    parser.add_argument("--limit", type=int, default=200)
    parser.add_argument("--output")
    args = parser.parse_args()

    context = load_pack_context(PROJECT_ROOT, args.pack_id)
    if context.candidate_csv is None:
        raise SystemExit("No candidate file")

    rows = build_review_queue(context.candidate_csv, limit=args.limit)
    output = Path(args.output) if args.output else (
        PROJECT_ROOT / "data" / "review_queues" / f"{args.pack_id}.csv"
    )
    output.parent.mkdir(parents=True, exist_ok=True)

    fields = list(rows[0].keys()) if rows else [
        "candidate_id", "latin_name", "native_name",
        "_provenance_score", "_provenance_status", "_provenance_reasons"
    ]
    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    print(f"{args.pack_id}: {len(rows)} review rows -> {output}")

if __name__ == "__main__":
    main()
