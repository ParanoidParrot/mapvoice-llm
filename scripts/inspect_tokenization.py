from __future__ import annotations

import argparse
import csv
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-name", default="sarvamai/sarvam-1")
    parser.add_argument("--limit", type=int, default=20)
    return parser.parse_args()


def main() -> None:
    from transformers import AutoTokenizer

    args = parse_args()

    tokenizer = AutoTokenizer.from_pretrained(
        args.model_name,
        trust_remote_code=True,
        use_fast=True,
    )

    source = PROJECT_ROOT / "data" / "raw" / "bengaluru_entities_v0.1.csv"
    with source.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))

    print(f"Model: {args.model_name}")
    print(f"{'English name':28} {'EN toks':>7}  {'Kannada name':24} {'KN toks':>7}")
    print("-" * 75)

    for row in rows[: args.limit]:
        en = row["english_name"]
        kn = row["kannada_name"]
        en_count = len(tokenizer.encode(en, add_special_tokens=False))
        kn_count = len(tokenizer.encode(kn, add_special_tokens=False))

        print(f"{en[:28]:28} {en_count:7d}  {kn[:24]:24} {kn_count:7d}")


if __name__ == "__main__":
    main()
