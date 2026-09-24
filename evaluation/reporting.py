from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

from .metrics import character_error_rate, exact_match


def summarize_predictions(rows: list[dict]) -> dict:
    count = max(len(rows), 1)

    valid_json = 0
    entity_exact = 0.0
    spoken_exact = 0.0
    cer_total = 0.0

    by_entity_type: dict[str, list[dict]] = defaultdict(list)

    for row in rows:
        target = row["target"]
        prediction = row.get("prediction") or {}

        valid_json += int(row.get("valid_json", True))
        entity_exact += exact_match(
            target.get("place_name"),
            prediction.get("place_name") or prediction.get("detected_entity"),
        )

        reference = target.get("spoken_form") or target.get("pronunciation_form") or ""
        hypothesis = (
            prediction.get("spoken_form")
            or prediction.get("pronunciation_form")
            or ""
        )
        spoken_exact += exact_match(reference, hypothesis)
        cer_total += character_error_rate(reference, hypothesis)

        by_entity_type[target.get("entity_type") or "unknown"].append(row)

    return {
        "examples": len(rows),
        "valid_json_rate": valid_json / count,
        "entity_exact_match": entity_exact / count,
        "spoken_form_exact_match": spoken_exact / count,
        "mean_character_error_rate": cer_total / count,
        "by_entity_type": {
            entity_type: {"examples": len(items)}
            for entity_type, items in sorted(by_entity_type.items())
        },
    }


def write_report(report: dict, path: str | Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
