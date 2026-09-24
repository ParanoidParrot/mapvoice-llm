from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from mapvoice_llm.adapter_registry import AdapterRegistry


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("adapter_id")
    args = parser.parse_args()

    registry = AdapterRegistry(
        PROJECT_ROOT / "configs" / "adapter_registry.json"
    )

    try:
        record = registry.promote(args.adapter_id)
    except KeyError:
        raise SystemExit(f"Adapter not found: {args.adapter_id}")

    print(json.dumps(record, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
