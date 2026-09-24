from __future__ import annotations

"""
Promote reviewed candidate rows into the v0.4 entity schema.

This script is intentionally strict:
- annotation_status must be "reviewed"
- kannada_name must be populated
- source_name must be populated
- it never overwrites an existing entity automatically
"""

import argparse
import csv
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CANDIDATES = PROJECT_ROOT / "data" / "seeds" / "bengaluru_candidates_v0.6.csv"
ENTITIES = PROJECT_ROOT / "data" / "raw" / "bengaluru_entities_v0.4.csv"


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main():
    args = parse_args()

    with CANDIDATES.open(newline="", encoding="utf-8") as handle:
        candidates = list(csv.DictReader(handle))

    with ENTITIES.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        entities = list(reader)
        fieldnames = list(reader.fieldnames or [])

    existing_names = {
        row["english_name"].strip().casefold()
        for row in entities
    }

    promotable = []
    for row in candidates:
        if row["annotation_status"].strip().lower() != "reviewed":
            continue
        if not row["kannada_name"].strip():
            continue
        if not row["source_name"].strip():
            continue
        if row["english_name"].strip().casefold() in existing_names:
            continue
        promotable.append(row)

    print(f"Promotable candidates: {len(promotable)}")

    for row in promotable:
        print(f"- {row['english_name']} -> {row['kannada_name']}")

    if args.dry_run or not promotable:
        return

    next_index = 1
    ids = {row["entity_id"] for row in entities}
    while f"blr_v06_{next_index:04d}" in ids:
        next_index += 1

    with ENTITIES.open("a", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)

        for row in promotable:
            entity_id = f"blr_v06_{next_index:04d}"
            next_index += 1

            writer.writerow({
                "entity_id": entity_id,
                "english_name": row["english_name"],
                "kannada_name": row["kannada_name"],
                "entity_type": row["entity_type"],
                "city": "Bengaluru",
                "language": "Kannada",
                "alternate_spellings": "",
                "morphemes": "",
                "suffix": "",
                "verification_status": "reviewed",
                "pronunciation_verified": "false",
                "source_name": row["source_name"],
                "source_url": row["source_url"],
                "source_type": "candidate-promotion",
                "reviewer": "",
                "notes": row["notes"],
            })

    print(f"Appended {len(promotable)} rows to {ENTITIES}")


if __name__ == "__main__":
    main()
