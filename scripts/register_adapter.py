from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from mapvoice_llm.adapter_registry import AdapterRegistry


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("adapter_id")
    parser.add_argument("adapter_path")
    parser.add_argument("--base-model", default="sarvamai/sarvam-1")
    parser.add_argument("--training-run-id")
    parser.add_argument("--notes")
    return parser.parse_args()


def main():
    args = parse_args()

    path = Path(args.adapter_path)
    if not path.is_absolute():
        path = (PROJECT_ROOT / path).resolve()

    record = AdapterRegistry(
        PROJECT_ROOT / "configs" / "adapter_registry.json"
    ).register({
        "adapter_id": args.adapter_id,
        "adapter_path": str(path),
        "base_model": args.base_model,
        "training_run_id": args.training_run_id,
        "notes": args.notes,
    })

    print(json.dumps(record, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
