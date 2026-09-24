from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))
sys.path.insert(0, str(PROJECT_ROOT))

from evaluation.metrics import character_error_rate
from mapvoice_llm.baseline import RuleBaseline
from mapvoice_llm.dataset import read_jsonl


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--test-file",
        default=str(PROJECT_ROOT / "data" / "processed" / "test.jsonl"),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    examples = read_jsonl(args.test_file)
    baseline = RuleBaseline(
        PROJECT_ROOT / "data" / "raw" / "bengaluru_entities_v0.1.csv"
    )

    exact = 0
    entity_exact = 0
    cer_total = 0.0

    for record in examples:
        prediction = baseline.predict(record["input"]["text"])
        target = record["target"]

        reference = target["pronunciation_form"]
        hypothesis = prediction.pronunciation_form or ""

        exact += int(reference == hypothesis)
        entity_exact += int(target["place_name"] == prediction.detected_entity)
        cer_total += character_error_rate(reference, hypothesis)

    count = max(len(examples), 1)
    report = {
        "backend": "rule-baseline",
        "examples": len(examples),
        "entity_exact_match": entity_exact / count,
        "pronunciation_exact_match": exact / count,
        "mean_character_error_rate": cer_total / count,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
