from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))
sys.path.insert(0, str(PROJECT_ROOT))

from evaluation.reporting import summarize_predictions, write_report
from mapvoice_llm.dataset import read_jsonl
from mapvoice_llm.model_backend import TransformersBackend


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-name", default="sarvamai/sarvam-1")
    parser.add_argument("--adapter-path")
    parser.add_argument(
        "--test-file",
        default=str(PROJECT_ROOT / "data" / "processed" / "test.jsonl"),
    )
    parser.add_argument(
        "--output",
        default=str(PROJECT_ROOT / "outputs" / "model_eval.json"),
    )
    parser.add_argument("--limit", type=int)
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    records = read_jsonl(args.test_file)
    if args.limit is not None:
        records = records[: args.limit]

    backend = TransformersBackend(
        model_name=args.model_name,
        adapter_path=args.adapter_path,
    )

    results = []

    for index, record in enumerate(records, start=1):
        model_result = backend.generate(**record["input"])
        prediction = model_result.data or {}

        results.append(
            {
                "example_id": record["example_id"],
                "entity_id": record["entity_id"],
                "input": record["input"],
                "target": record["target"],
                "prediction": prediction,
                "valid_json": model_result.valid_json,
                "error": model_result.error,
                "raw_text": model_result.raw_text,
            }
        )

        print(
            f"[{index}/{len(records)}] "
            f"{record['entity_id']} "
            f"valid_json={model_result.valid_json}"
        )

    report = {
        "model_name": args.model_name,
        "adapter_path": args.adapter_path,
        "summary": summarize_predictions(results),
        "results": results,
    }

    write_report(report, args.output)

    print()
    print(json.dumps(report["summary"], ensure_ascii=False, indent=2))
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
