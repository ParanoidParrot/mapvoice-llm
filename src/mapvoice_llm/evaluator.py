from __future__ import annotations

import time
from pathlib import Path

from evaluation.metrics import character_error_rate, exact_match
from .baseline import RuleBaseline
from .dataset import read_jsonl
from .model_backend import TransformersBackend


def _spoken_form(target: dict) -> str:
    return target.get("spoken_form") or target.get("pronunciation_form") or ""


def evaluate_rule(
    *,
    entity_csv: str | Path,
    test_file: str | Path,
    limit: int | None = None,
) -> dict:
    rows = read_jsonl(test_file)
    if limit is not None:
        rows = rows[:limit]

    baseline = RuleBaseline(entity_csv)

    results = []
    entity_exact_total = 0.0
    spoken_exact_total = 0.0
    cer_total = 0.0

    started = time.perf_counter()

    for row in rows:
        prediction = baseline.predict(row["input"]["text"])
        target = row["target"]
        reference = _spoken_form(target)
        hypothesis = prediction.spoken_form or prediction.pronunciation_form or ""

        entity_exact = exact_match(
            target.get("place_name"),
            prediction.detected_entity,
        )
        spoken_exact = exact_match(reference, hypothesis)
        cer = character_error_rate(reference, hypothesis)

        entity_exact_total += entity_exact
        spoken_exact_total += spoken_exact
        cer_total += cer

        results.append(
            {
                "example_id": row["example_id"],
                "entity_id": row["entity_id"],
                "input": row["input"],
                "target": target,
                "prediction": prediction.model_dump(),
                "metrics": {
                    "entity_exact": entity_exact,
                    "spoken_exact": spoken_exact,
                    "character_error_rate": cer,
                },
            }
        )

    count = max(len(rows), 1)

    return {
        "backend": "rule",
        "examples": len(rows),
        "summary": {
            "entity_exact_match": entity_exact_total / count,
            "spoken_form_exact_match": spoken_exact_total / count,
            "mean_character_error_rate": cer_total / count,
            "elapsed_ms": round((time.perf_counter() - started) * 1000, 2),
        },
        "results": results,
    }


def evaluate_model(
    *,
    model_name: str,
    adapter_path: str | None,
    test_file: str | Path,
    limit: int | None = None,
) -> dict:
    rows = read_jsonl(test_file)
    if limit is not None:
        rows = rows[:limit]

    backend = TransformersBackend(
        model_name=model_name,
        adapter_path=adapter_path,
    )

    results = []
    valid_json_total = 0
    entity_exact_total = 0.0
    spoken_exact_total = 0.0
    cer_total = 0.0

    started = time.perf_counter()

    for row in rows:
        generated = backend.generate(**row["input"])
        prediction = generated.data or {}
        target = row["target"]

        reference = _spoken_form(target)
        hypothesis = (
            prediction.get("spoken_form")
            or prediction.get("pronunciation_form")
            or ""
        )

        valid_json_total += int(generated.valid_json)
        entity_exact_total += exact_match(
            target.get("place_name"),
            prediction.get("place_name"),
        )
        spoken_exact_total += exact_match(reference, hypothesis)
        cer_total += character_error_rate(reference, hypothesis)

        results.append(
            {
                "example_id": row["example_id"],
                "entity_id": row["entity_id"],
                "input": row["input"],
                "target": target,
                "prediction": prediction,
                "valid_json": generated.valid_json,
                "error": generated.error,
                "raw_text": generated.raw_text,
            }
        )

    count = max(len(rows), 1)

    return {
        "backend": "model",
        "model_name": model_name,
        "adapter_path": adapter_path,
        "examples": len(rows),
        "summary": {
            "valid_json_rate": valid_json_total / count,
            "entity_exact_match": entity_exact_total / count,
            "spoken_form_exact_match": spoken_exact_total / count,
            "mean_character_error_rate": cer_total / count,
            "elapsed_ms": round((time.perf_counter() - started) * 1000, 2),
        },
        "results": results,
    }
