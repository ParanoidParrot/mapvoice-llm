from __future__ import annotations
import argparse
import csv
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from mapvoice_llm.pack_schema import GENERIC_CANDIDATE_FIELDS
from mapvoice_llm.regional_packs import RegionalPackRegistry

EXTRA_FIELDS = [
    "alternate_names", "latitude", "longitude", "source_id",
    "source_record_id", "source_license", "source_retrieved_at",
    "source_snapshot_sha256", "provenance_status", "review_priority"
]

def migrate(path: Path) -> None:
    if not path.exists():
        return
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
        fields = list(reader.fieldnames or [])

    # Preserve legacy fields; append provenance fields only.
    for field in EXTRA_FIELDS:
        if field not in fields:
            fields.append(field)

    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})
    tmp.replace(path)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pack-id")
    parser.add_argument("--all", action="store_true")
    args = parser.parse_args()

    registry = RegionalPackRegistry(PROJECT_ROOT / "configs/regional_packs.json")
    packs = registry.list() if args.all else [registry.get(args.pack_id)]
    for pack in packs:
        if pack.candidate_file:
            migrate(PROJECT_ROOT / pack.candidate_file)
            print(f"{pack.pack_id}: migrated")

if __name__ == "__main__":
    main()
