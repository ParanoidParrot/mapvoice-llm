from __future__ import annotations
import argparse, csv, re
from collections import Counter
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
KANNADA_RE = re.compile(r"[\u0C80-\u0CFF]")
VALID_STATUS = {"unverified","reviewed","verified","rejected"}

REQUIRED = {
    "entity_id","english_name","kannada_name","entity_type","city","language",
    "alternate_spellings","morphemes","suffix",
    "verification_status","pronunciation_verified",
    "source_name","source_url","source_type","reviewer","notes",
}

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--input", default=str(PROJECT_ROOT / "data/raw/bengaluru_entities_v0.4.csv"))
    return p.parse_args()

def main():
    args = parse_args()
    with Path(args.input).open(newline="", encoding="utf-8") as h:
        reader = csv.DictReader(h)
        rows = list(reader)
        columns = set(reader.fieldnames or [])

    errors, warnings = [], []
    missing = REQUIRED - columns
    if missing:
        errors.append(f"Missing columns: {sorted(missing)}")

    ids = [r["entity_id"].strip() for r in rows]
    dup_ids = [x for x,c in Counter(ids).items() if c > 1]
    if dup_ids:
        errors.append(f"Duplicate entity IDs: {dup_ids}")

    names = [r["english_name"].strip().casefold() for r in rows]
    dup_names = [x for x,c in Counter(names).items() if c > 1]
    if dup_names:
        warnings.append(f"Duplicate English names: {dup_names}")

    for num,row in enumerate(rows, start=2):
        eid = row.get("entity_id","")
        kn = row.get("kannada_name","").strip()
        if kn and not KANNADA_RE.search(kn):
            warnings.append(f"row {num} ({eid}): kannada_name has no Kannada codepoint")

        status = row.get("verification_status","").strip().lower()
        if status not in VALID_STATUS:
            errors.append(f"row {num} ({eid}): invalid verification_status={status!r}")

        pv = row.get("pronunciation_verified","").strip().lower()
        if pv not in {"true","false"}:
            errors.append(f"row {num} ({eid}): pronunciation_verified must be true/false")

        if status == "verified" and not row.get("source_name","").strip():
            warnings.append(f"row {num} ({eid}): verified row has no source_name")
        if pv == "true" and not row.get("reviewer","").strip():
            warnings.append(f"row {num} ({eid}): pronunciation verified without reviewer")

    print(f"Rows: {len(rows)}")
    print(f"Errors: {len(errors)}")
    print(f"Warnings: {len(warnings)}")
    for x in errors: print("ERROR:", x)
    for x in warnings: print("WARN :", x)
    if errors:
        raise SystemExit(1)

if __name__ == "__main__":
    main()
