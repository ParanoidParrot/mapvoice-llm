from __future__ import annotations

import argparse
import json
from pathlib import Path


METRICS = [
    "valid_json_rate",
    "entity_exact_match",
    "spoken_form_exact_match",
    "pronunciation_exact_match",
    "mean_character_error_rate",
]


def load(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("reports", nargs="+", help="JSON evaluation reports")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rows = []

    for path in args.reports:
        report = load(path)
        summary = report.get("summary", report)
        rows.append(
            {
                "file": path,
                "model_name": report.get("model_name")
                or summary.get("backend")
                or "unknown",
                **{metric: summary.get(metric) for metric in METRICS},
            }
        )

    print(json.dumps(rows, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
