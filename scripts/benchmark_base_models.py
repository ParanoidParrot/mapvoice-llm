from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from mapvoice_llm.base_model_benchmark import benchmark_plan, run_base_model_benchmark
from mapvoice_llm.base_model_registry import BaseModelRegistry


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pack-id", default="blr-kn")
    parser.add_argument("--policy", default="labeled")
    parser.add_argument("--limit", type=int)
    parser.add_argument(
        "--models",
        help="Comma-separated model keys. Default: all benchmark-enabled models.",
    )
    parser.add_argument("--plan-only", action="store_true")
    parser.add_argument("--tokenizer-only", action="store_true")
    args = parser.parse_args()

    registry = BaseModelRegistry(
        PROJECT_ROOT / "configs" / "base_models.json"
    )

    if args.models:
        models = [
            registry.get(key.strip())
            for key in args.models.split(",")
            if key.strip()
        ]
    else:
        models = registry.benchmark_models()

    if args.plan_only:
        result = benchmark_plan(
            project_root=PROJECT_ROOT,
            pack_id=args.pack_id,
            models=models,
            policy_id=args.policy,
            limit=args.limit,
        )
    else:
        result = run_base_model_benchmark(
            project_root=PROJECT_ROOT,
            pack_id=args.pack_id,
            models=models,
            policy_id=args.policy,
            limit=args.limit,
            tokenizer_only=args.tokenizer_only,
        )

    print(json.dumps(
        result,
        ensure_ascii=False,
        indent=2,
    ))


if __name__ == "__main__":
    main()
