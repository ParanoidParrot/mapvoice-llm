from __future__ import annotations
import csv
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SOURCE = PROJECT_ROOT / "data/raw/bengaluru_entities_v0.4.csv"
OUTPUT = PROJECT_ROOT / "outputs/annotation_queue.csv"

FIELDS = [
    "entity_id","english_name","kannada_name","entity_type",
    "alternate_spellings","morphemes","suffix",
    "verification_status","pronunciation_verified",
    "source_name","source_url","source_type","reviewer","notes",
]

def main():
    with SOURCE.open(newline="", encoding="utf-8") as h:
        rows = list(csv.DictReader(h))
    queue = [
        r for r in rows
        if r["verification_status"] in {"unverified","reviewed"}
        or r["pronunciation_verified"].lower() != "true"
    ]
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", newline="", encoding="utf-8") as h:
        w = csv.DictWriter(h, fieldnames=FIELDS)
        w.writeheader()
        for row in queue:
            w.writerow({f: row.get(f,"") for f in FIELDS})
    print(f"Wrote {len(queue)} rows to {OUTPUT}")

if __name__ == "__main__":
    main()
