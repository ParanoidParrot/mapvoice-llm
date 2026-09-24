from __future__ import annotations

import json
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from mapvoice_llm.experiment_store import ExperimentStore


def main() -> None:
    store = ExperimentStore(PROJECT_ROOT / "outputs" / "experiments")
    experiments = store.list(limit=20)

    summary = [
        {
            "experiment_id": item["experiment_id"],
            "backend": item.get("backend"),
            "model_name": item.get("model_name"),
            "examples": item.get("examples"),
            "summary": item.get("summary"),
        }
        for item in experiments
    ]

    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
