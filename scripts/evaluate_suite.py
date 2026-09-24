from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))
sys.path.insert(0, str(PROJECT_ROOT))

from mapvoice_llm.evaluation_suites import EvaluationSuiteRegistry
from mapvoice_llm.experiment_store import ExperimentStore
from mapvoice_llm.suite_evaluator import evaluate_suite_rule


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--suite",
        default="entity-held-out",
        choices=[
            "entity-held-out",
            "lexicon-known",
            "morphological-hard",
            "generated-hard-holdout",
        ],
    )
    parser.add_argument("--limit", type=int, default=10)
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    registry = EvaluationSuiteRegistry(PROJECT_ROOT)
    suite = registry.get(args.suite)

    report = evaluate_suite_rule(
        entity_csv=PROJECT_ROOT / "data/raw/bengaluru_entities_v0.4.csv",
        suite_path=suite["absolute_path"],
        suite_kind=suite["kind"],
        limit=args.limit,
    )

    report["suite_id"] = suite["id"]
    report["suite_label"] = suite["label"]

    stored = ExperimentStore(
        PROJECT_ROOT / "outputs/experiments"
    ).save(report)

    print(json.dumps(stored["summary"], ensure_ascii=False, indent=2))
    print(f"Suite: {suite['label']}")
    print(f"Experiment: {stored['experiment_id']}")


if __name__ == "__main__":
    main()
