from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from mapvoice_llm.runtime_compat import required_training_package_checks


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--model-name",
        default="sarvamai/sarvam-1",
    )
    parser.add_argument(
        "--use-fast",
        action="store_true",
        help="Require the fast tokenizer.",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    failed = [
        item
        for item in required_training_package_checks()
        if not item.ok
    ]

    if failed:
        print("Training dependencies are incomplete:")
        for item in failed:
            print(f"- {item.message}")
        raise SystemExit(1)

    from mapvoice_llm.tokenizer_loader import load_tokenizer

    print(f"Loading tokenizer: {args.model_name}")
    print(f"use_fast={args.use_fast}")

    try:
        tokenizer, tokenizer_info = load_tokenizer(
            args.model_name,
            trust_remote_code=True,
            prefer_fast=args.use_fast,
        )
    except Exception as exc:
        print()
        print("Tokenizer load failed.")
        print(f"{type(exc).__name__}: {exc}")
        print()
        print("Common dependency fix:")
        print("  python -m pip install -U protobuf sentencepiece")
        raise SystemExit(1)

    sample = "Continue towards Bengaluru."
    encoded = tokenizer(sample)

    print(json.dumps({
        "tokenizer_class": type(tokenizer).__name__,
        "model_name": args.model_name,
        "requested_fast": args.use_fast,
        "use_fast": tokenizer_info["use_fast"],
        "fallback_used": tokenizer_info["fallback_used"],
        "sample_input_ids": encoded.get("input_ids", [])[:20],
    }, indent=2))
    print("Tokenizer loaded successfully.")


if __name__ == "__main__":
    main()
