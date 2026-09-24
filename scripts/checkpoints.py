from __future__ import annotations

import json
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from mapvoice_llm.checkpoints import discover_checkpoints


def main():
    rows = discover_checkpoints(PROJECT_ROOT / "artifacts")
    print(json.dumps(rows, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
