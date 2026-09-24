from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))
sys.path.insert(0, str(PROJECT_ROOT))

from mapvoice_llm.evaluator import evaluate_rule
from mapvoice_llm.experiment_store import ExperimentStore


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=10)
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    report = evaluate_rule(
        entity_csv=PROJECT_ROOT / "data/raw/bengaluru_entities_v0.4.csv",
        test_file=PROJECT_ROOT / "data/processed/test.jsonl",
        limit=args.limit,
    )

    stored = ExperimentStore(
        PROJECT_ROOT / "outputs" / "experiments"
    ).save(report)

    print(json.dumps(stored["summary"], ensure_ascii=False, indent=2))
    print(f"Experiment: {stored['experiment_id']}")


if __name__ == "__main__":
    main()
