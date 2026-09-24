from __future__ import annotations
import argparse, json, sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from mapvoice_llm.dataset import (
    generate_examples, read_entities, split_by_entity, write_jsonl
)

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--entities", default=str(PROJECT_ROOT / "data/raw/bengaluru_entities_v0.4.csv"))
    p.add_argument("--verified-only", action="store_true")
    p.add_argument("--pronunciation-verified-only", action="store_true")
    p.add_argument("--seed", type=int, default=42)
    return p.parse_args()

def main():
    args = parse_args()
    entities = read_entities(args.entities)
    examples = generate_examples(
        entities,
        verified_only=args.verified_only,
        pronunciation_verified_only=args.pronunciation_verified_only,
    )
    if not examples:
        raise SystemExit("No training examples generated; check verification filters.")

    train,val,test = split_by_entity(examples, seed=args.seed)
    out = PROJECT_ROOT / "data/processed"
    write_jsonl(examples, out/"navigation_examples.jsonl")
    write_jsonl(train, out/"train.jsonl")
    write_jsonl(val, out/"validation.jsonl")
    write_jsonl(test, out/"test.jsonl")

    count_entities = lambda rows: len({x["entity_id"] for x in rows})
    manifest = {
        "dataset_version": "0.4",
        "entity_file": str(Path(args.entities).relative_to(PROJECT_ROOT)),
        "split_strategy": "entity-level",
        "seed": args.seed,
        "filters": {
            "verified_only": args.verified_only,
            "pronunciation_verified_only": args.pronunciation_verified_only,
        },
        "source_entities": len(entities),
        "included_entities": count_entities(examples),
        "total_examples": len(examples),
        "splits": {
            "train": {"examples": len(train), "entities": count_entities(train)},
            "validation": {"examples": len(val), "entities": count_entities(val)},
            "test": {"examples": len(test), "entities": count_entities(test)},
        },
    }
    (out/"manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
