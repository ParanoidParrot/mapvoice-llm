from __future__ import annotations

import json
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from mapvoice_llm.readiness import training_readiness


def main() -> None:
    report = training_readiness(
        PROJECT_ROOT / "data/raw/bengaluru_entities_v0.4.csv",
        PROJECT_ROOT / "data/seeds/bengaluru_candidates_v0.6.csv",
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
