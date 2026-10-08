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
from mapvoice_llm.provenance import score_candidate

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pack-id", required=True)
    args = parser.parse_args()

    context = load_pack_context(PROJECT_ROOT, args.pack_id)
    with context.candidate_csv.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))

    scores = [score_candidate(row) for row in rows]
    print(json.dumps({
        "pack_id": args.pack_id,
        "candidates": len(rows),
        "provenance_status": dict(Counter(x.status for x in scores)),
        "average_score": round(sum(x.score for x in scores) / len(scores), 2) if scores else 0,
        "with_native_name": sum(bool((r.get("native_name") or r.get("kannada_name") or "").strip()) for r in rows),
        "reviewed": sum(r.get("annotation_status") == "reviewed" for r in rows),
    }, indent=2))

if __name__ == "__main__":
    main()
