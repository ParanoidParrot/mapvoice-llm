from __future__ import annotations

import json
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from mapvoice_llm.training_runs import TrainingRunStore


def main():
    runs = TrainingRunStore(
        PROJECT_ROOT / "outputs" / "training_runs"
    ).list(limit=50)

    print(json.dumps(runs, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
