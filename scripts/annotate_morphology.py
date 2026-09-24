from __future__ import annotations
import argparse, csv, sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))
from mapvoice_llm.morphology import guess_suffix

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--input", default=str(PROJECT_ROOT / "data/raw/bengaluru_entities_v0.4.csv"))
    p.add_argument("--output", default=str(PROJECT_ROOT / "data/raw/bengaluru_entities_v0.4_morphology.csv"))
    return p.parse_args()

def main():
    args = parse_args()
    with Path(args.input).open(newline="", encoding="utf-8") as h:
        rows = list(csv.DictReader(h))
        fields = list(rows[0].keys()) if rows else []

    for f in ("suffix_guess","stem_guess","morphology_guess_confidence"):
        if f not in fields:
            fields.append(f)

    for row in rows:
        guess = guess_suffix(row["english_name"])
        row["suffix_guess"] = guess.suffix or ""
        row["stem_guess"] = guess.stem
        row["morphology_guess_confidence"] = guess.confidence

    with Path(args.output).open("w", newline="", encoding="utf-8") as h:
        w = csv.DictWriter(h, fieldnames=fields)
        w.writeheader(); w.writerows(rows)
    print(f"Wrote {args.output}")

if __name__ == "__main__":
    main()
