from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))


def command_build():
    from mapvoice_llm.dataset import (
        generate_examples,
        read_entities,
        split_by_entity,
        write_jsonl,
    )

    raw = PROJECT_ROOT / "data" / "raw" / "bengaluru_entities_v0.1.csv"
    processed = PROJECT_ROOT / "data" / "processed"

    entities = read_entities(raw)
    examples = generate_examples(entities)
    train, validation, test = split_by_entity(examples)

    write_jsonl(examples, processed / "navigation_examples.jsonl")
    write_jsonl(train, processed / "train.jsonl")
    write_jsonl(validation, processed / "validation.jsonl")
    write_jsonl(test, processed / "test.jsonl")

    print(
        json.dumps(
            {
                "entities": len(entities),
                "examples": len(examples),
                "train": len(train),
                "validation": len(validation),
                "test": len(test),
            },
            indent=2,
        )
    )


def command_predict(text: str):
    from mapvoice_llm.baseline import RuleBaseline

    baseline = RuleBaseline(
        PROJECT_ROOT / "data" / "raw" / "bengaluru_entities_v0.1.csv"
    )
    print(
        json.dumps(
            baseline.predict(text).model_dump(),
            ensure_ascii=False,
            indent=2,
        )
    )


def main() -> None:
    parser = argparse.ArgumentParser(prog="mapvoice")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("build", help="build processed dataset")

    predict = sub.add_parser("predict", help="run rule-baseline prediction")
    predict.add_argument("text")

    args = parser.parse_args()

    if args.command == "build":
        command_build()
    elif args.command == "predict":
        command_predict(args.text)


if __name__ == "__main__":
    main()
