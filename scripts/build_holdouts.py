from __future__ import annotations
import argparse, csv, json, random
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--entities", default=str(PROJECT_ROOT / "data/raw/bengaluru_entities_v0.4.csv"))
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--hard-size", type=int, default=10)
    return p.parse_args()

def main():
    args = parse_args()
    with Path(args.entities).open(newline="", encoding="utf-8") as h:
        rows = [r for r in csv.DictReader(h) if r["verification_status"] != "rejected"]

    with_suffix = [r for r in rows if r.get("suffix")]
    without_suffix = [r for r in rows if not r.get("suffix")]
    rng = random.Random(args.seed)
    rng.shuffle(with_suffix); rng.shuffle(without_suffix)

    half = args.hard_size // 2
    selected = with_suffix[:half] + without_suffix[:args.hard_size-half]

    out = PROJECT_ROOT / "data/evaluation/generated_hard_holdout.jsonl"
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as h:
        for r in selected:
            h.write(json.dumps({
                "suite": "generated-hard-holdout",
                "entity_id": r["entity_id"],
                "english_name": r["english_name"],
                "kannada_name": r["kannada_name"],
                "entity_type": r["entity_type"],
                "suffix": r.get("suffix") or None,
                "verification_status": r["verification_status"],
                "instruction": f"Continue towards {r['english_name']}.",
            }, ensure_ascii=False) + "\n")
    print(f"Wrote {len(selected)} rows to {out}")

if __name__ == "__main__":
    main()
