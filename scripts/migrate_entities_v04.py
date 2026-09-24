from __future__ import annotations
import csv
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
OLD = PROJECT_ROOT / "data/raw/bengaluru_entities_v0.1.csv"
NEW = PROJECT_ROOT / "data/raw/bengaluru_entities_v0.4.csv"

FIELDS = [
    "entity_id","english_name","kannada_name","entity_type","city","language",
    "alternate_spellings","morphemes","suffix",
    "verification_status","pronunciation_verified",
    "source_name","source_url","source_type","reviewer","notes",
]

def main():
    with OLD.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))

    with NEW.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow({
                "entity_id": row["entity_id"],
                "english_name": row["english_name"],
                "kannada_name": row["kannada_name"],
                "entity_type": row["entity_type"],
                "city": row["city"],
                "language": row["language"],
                "alternate_spellings": row.get("alternate_spellings",""),
                "morphemes": row.get("morphemes",""),
                "suffix": row.get("suffix",""),
                "verification_status": "unverified",
                "pronunciation_verified": "false",
                "source_name": "",
                "source_url": "",
                "source_type": "",
                "reviewer": "",
                "notes": "Migrated from v0.1 seed row",
            })
    print(f"Wrote {NEW}")

if __name__ == "__main__":
    main()
