from __future__ import annotations

import json
from pathlib import Path


def build_improvement_rows(experiment: dict) -> list[dict]:
    rows = []

    for result in experiment.get("results") or []:
        failures = result.get("failures") or []

        if not failures:
            continue

        rows.append(
            {
                "example_id": result.get("example_id"),
                "entity_id": result.get("entity_id"),
                "suite_id": experiment.get("suite_id"),
                "backend": experiment.get("backend"),
                "text": result.get("text") or (result.get("input") or {}).get("text"),
                "target": result.get("target"),
                "prediction": result.get("prediction"),
                "failures": failures,
                "metrics": result.get("metrics"),
            }
        )

    return rows


def write_jsonl(rows: list[dict], path: str | Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
