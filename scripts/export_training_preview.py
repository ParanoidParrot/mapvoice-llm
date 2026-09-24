from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from mapvoice_llm.dataset import read_jsonl
from mapvoice_llm.prompts import format_sft_example


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input",
        default=str(PROJECT_ROOT / "data" / "processed" / "train.jsonl"),
    )
    parser.add_argument(
        "--output",
        default=str(PROJECT_ROOT / "outputs" / "training_preview.txt"),
    )
    parser.add_argument("--limit", type=int, default=5)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rows = read_jsonl(args.input)[: args.limit]

    chunks = []
    for index, row in enumerate(rows, start=1):
        formatted = format_sft_example(row)
        chunks.append(
            f"===== EXAMPLE {index} =====\n"
            f"{formatted['prompt']}{formatted['completion']}\n"
        )

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(chunks), encoding="utf-8")
    print(f"Wrote {output}")


if __name__ == "__main__":
    main()
