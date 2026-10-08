from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from mapvoice_llm.pack_context import load_pack_context


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pack-id")
    args = parser.parse_args()

    context = load_pack_context(PROJECT_ROOT, args.pack_id)
    entities = context.entity_repository.list()

    print(json.dumps({
        "pack": context.pack.to_dict(),
        "entity_file": str(context.entity_csv.relative_to(PROJECT_ROOT)),
        "candidate_file": (
            str(context.candidate_csv.relative_to(PROJECT_ROOT))
            if context.candidate_csv
            else None
        ),
        "entity_count": len(entities),
        "verified_count": sum(
            entity.verification_status == "verified"
            for entity in entities
        ),
        "pronunciation_verified_count": sum(
            entity.pronunciation_verified
            for entity in entities
        ),
        "entity_types": sorted({
            entity.entity_type
            for entity in entities
            if entity.entity_type
        }),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
