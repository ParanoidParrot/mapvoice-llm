from __future__ import annotations

import argparse
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from mapvoice_llm.experiment_store import ExperimentStore
from mapvoice_llm.improvement_dataset import (
    build_improvement_rows,
    write_jsonl,
)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("experiment_id")
    parser.add_argument("--output")
    return parser.parse_args()


def main():
    args = parse_args()

    store = ExperimentStore(PROJECT_ROOT / "outputs" / "experiments")
    experiment = store.get(args.experiment_id)

    if experiment is None:
        raise SystemExit(f"Experiment not found: {args.experiment_id}")

    rows = build_improvement_rows(experiment)

    output = (
        Path(args.output)
        if args.output
        else PROJECT_ROOT
        / "outputs"
        / "improvement_datasets"
        / f"{args.experiment_id}_failures.jsonl"
    )

    write_jsonl(rows, output)

    print(f"Rows: {len(rows)}")
    print(f"Wrote: {output}")


if __name__ == "__main__":
    main()
