from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from mapvoice_llm.kannada_adapter_pipeline import (
    evaluate_kannada_adapter,
    lifecycle_status,
    prepare_kannada_adapter,
    run_training,
)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", default="local-mac")
    parser.add_argument("--dataset-policy", default="labeled")
    parser.add_argument("--adapter-version", default="v1")
    parser.add_argument("--model-name")
    parser.add_argument("--limit", type=int)

    parser.add_argument("--prepare", action="store_true")
    parser.add_argument("--train", action="store_true")
    parser.add_argument("--evaluate", action="store_true")
    parser.add_argument("--promote-if-passes", action="store_true")
    parser.add_argument("--export", action="store_true")
    parser.add_argument("--status", action="store_true")
    parser.add_argument(
        "--all",
        action="store_true",
        help="Prepare, train, evaluate and export in sequence.",
    )
    args = parser.parse_args()

    if args.status:
        print(json.dumps(
            lifecycle_status(
                project_root=PROJECT_ROOT,
            ),
            ensure_ascii=False,
            indent=2,
        ))
        return

    do_prepare = (
        args.prepare
        or args.train
        or args.evaluate
        or args.all
        or not any([
            args.prepare,
            args.train,
            args.evaluate,
            args.status,
            args.all,
        ])
    )

    prepared = None
    if do_prepare:
        prepared = prepare_kannada_adapter(
            project_root=PROJECT_ROOT,
            profile_id=args.profile,
            dataset_policy=args.dataset_policy,
            adapter_version=args.adapter_version,
            model_name=args.model_name,
        )
        print("PREPARE")
        print(json.dumps(
            prepared,
            ensure_ascii=False,
            indent=2,
        ))

    if args.train or args.all:
        training = run_training(
            project_root=PROJECT_ROOT,
            plan=prepared["training_plan"],
            dataset_policy=args.dataset_policy,
        )
        print("TRAIN")
        print(json.dumps(
            training,
            ensure_ascii=False,
            indent=2,
        ))

    if args.evaluate or args.all:
        adapter_id = prepared["training_plan"]["adapter_id"]
        evaluated = evaluate_kannada_adapter(
            project_root=PROJECT_ROOT,
            adapter_id=adapter_id,
            dataset_policy=args.dataset_policy,
            limit=args.limit,
            promote_if_passes=args.promote_if_passes,
            export_bundle=(args.export or args.all),
        )
        print("EVALUATE")
        print(json.dumps(
            evaluated,
            ensure_ascii=False,
            indent=2,
        ))


if __name__ == "__main__":
    main()
