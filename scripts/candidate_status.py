from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from mapvoice_llm.candidates import CandidateRepository
from mapvoice_llm.pack_context import load_pack_context


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pack-id")
    args = parser.parse_args()

    context = load_pack_context(
        PROJECT_ROOT,
        args.pack_id,
    )
    if context.candidate_csv is None:
        raise SystemExit("Pack has no candidate file")

    repo = CandidateRepository(
        context.candidate_csv
    )
    rows = repo.list(limit=100000)

    print(json.dumps({
        "pack_id": context.pack.pack_id,
        "candidates": len(rows),
        "annotation_status": dict(
            Counter(
                row.get("annotation_status")
                for row in rows
            )
        ),
        "entity_types": dict(
            Counter(
                row.get("entity_type")
                for row in rows
            )
        ),
        "with_native_name": sum(
            bool(
                (
                    row.get("native_name")
                    or ""
                ).strip()
            )
            for row in rows
        ),
        "with_source": sum(
            bool(
                row.get(
                    "source_name",
                    "",
                ).strip()
            )
            for row in rows
        ),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
