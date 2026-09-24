from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from collections import Counter

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from mapvoice_llm.experiment_store import ExperimentStore


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("experiment_id")
    return parser.parse_args()


def main():
    args = parse_args()

    experiment = ExperimentStore(
        PROJECT_ROOT / "outputs" / "experiments"
    ).get(args.experiment_id)

    if experiment is None:
        raise SystemExit(f"Experiment not found: {args.experiment_id}")

    counter = Counter()
    examples = []

    for row in experiment.get("results") or []:
        failures = row.get("failures") or []
        for failure in failures:
            counter[failure["code"]] += 1
        if failures:
            examples.append({
                "example_id": row.get("example_id"),
                "text": row.get("text"),
                "failures": failures,
            })

    print(json.dumps({
        "experiment_id": args.experiment_id,
        "suite_id": experiment.get("suite_id"),
        "backend": experiment.get("backend"),
        "failure_counts": dict(counter.most_common()),
        "examples_with_failures": len(examples),
        "examples": examples[:20],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
