from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from mapvoice_llm.benchmark_protocol import BenchmarkProtocol
from mapvoice_llm.benchmark_report import compare_result_sets, write_report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--first", required=True)
    parser.add_argument("--second", required=True)
    parser.add_argument("--first-name", default="first")
    parser.add_argument("--second-name", default="second")
    parser.add_argument("--output")
    args = parser.parse_args()

    first = json.loads(
        Path(args.first).read_text(
            encoding="utf-8"
        )
    )
    second = json.loads(
        Path(args.second).read_text(
            encoding="utf-8"
        )
    )

    protocol = BenchmarkProtocol.load(
        PROJECT_ROOT
        / "configs"
        / "benchmark_protocol.json"
    )

    report = compare_result_sets(
        protocol=protocol,
        first_name=args.first_name,
        first_results=first["results"],
        second_name=args.second_name,
        second_results=second["results"],
    )

    output = (
        Path(args.output)
        if args.output
        else (
            PROJECT_ROOT
            / "outputs"
            / "benchmark_comparisons"
            / "comparison.json"
        )
    )

    write_report(
        report,
        output,
    )

    print(json.dumps(
        report,
        ensure_ascii=False,
        indent=2,
    ))


if __name__ == "__main__":
    main()
