from __future__ import annotations

import time
from pathlib import Path

from evaluation.metrics import character_error_rate, exact_match
from .baseline import RuleBaseline
from .model_backend import TransformersBackend
from .dataset import read_jsonl
from .evaluation_suites import read_evaluation_jsonl
from .failure_taxonomy import classify_failure
from .failure_reporting import summarize_failures


def _prediction_dict_from_rule(prediction) -> dict:
    return {
        "place_name": prediction.detected_entity,
        "place_name_kn": prediction.entity_kannada,
        "spoken_form": prediction.spoken_form or prediction.pronunciation_form,
        "entity_type": prediction.entity_type,
        "source": prediction.source,
    }


def _target_from_eval_row(row: dict) -> dict:
    return {
        "place_name": row.get("english_name"),
        "place_name_kn": row.get("kannada_name"),
        "spoken_form": row.get("kannada_name"),
        "entity_type": row.get("entity_type"),
    }


def _instruction_from_eval_row(row: dict) -> str:
    return row.get("instruction") or f"Continue towards {row.get('english_name', '')}."


def _evaluate_rows(
    *,
    rows: list[dict],
    predict,
    valid_json_default: bool,
) -> dict:
    results = []
    entity_exact_total = 0.0
    spoken_exact_total = 0.0
    cer_total = 0.0
    valid_json_total = 0

    started = time.perf_counter()

    for index, row in enumerate(rows):
        if "input" in row and "target" in row:
            text = row["input"]["text"]
            target = row["target"]
            entity_id = row.get("entity_id")
            example_id = row.get("example_id", f"row_{index:04d}")
        else:
            text = _instruction_from_eval_row(row)
            target = _target_from_eval_row(row)
            entity_id = row.get("entity_id")
            example_id = row.get("entity_id", f"row_{index:04d}")

        output = predict(text)
        prediction = output["prediction"]
        valid_json = output.get("valid_json", valid_json_default)

        reference = target.get("spoken_form") or target.get("pronunciation_form") or ""
        hypothesis = (
            prediction.get("spoken_form")
            or prediction.get("pronunciation_form")
            or ""
        )

        entity_exact = exact_match(
            target.get("place_name"),
            prediction.get("place_name") or prediction.get("detected_entity"),
        )
        spoken_exact = exact_match(reference, hypothesis)
        cer = character_error_rate(reference, hypothesis)

        entity_exact_total += entity_exact
        spoken_exact_total += spoken_exact
        cer_total += cer
        valid_json_total += int(valid_json)

        row_metadata = {}
        if "metadata" in row:
            row_metadata.update(row.get("metadata") or {})
        if "suite" in row:
            row_metadata["suite"] = row.get("suite")
        if "suffix" in row:
            row_metadata["suffix"] = row.get("suffix")

        failures = classify_failure(
            target=target,
            prediction=prediction,
            valid_json=valid_json,
            cer=cer,
            metadata=row_metadata,
        )

        results.append(
            {
                "example_id": example_id,
                "entity_id": entity_id,
                "text": text,
                "target": target,
                "prediction": prediction,
                "valid_json": valid_json,
                "metadata": row_metadata,
                "metrics": {
                    "entity_exact": entity_exact,
                    "spoken_exact": spoken_exact,
                    "character_error_rate": cer,
                },
                "failures": [
                    {
                        "code": failure.code,
                        "label": failure.label,
                        "severity": failure.severity,
                        "details": failure.details,
                    }
                    for failure in failures
                ],
            }
        )

    count = max(len(rows), 1)

    summary = {
        "valid_json_rate": valid_json_total / count,
        "entity_exact_match": entity_exact_total / count,
        "spoken_form_exact_match": spoken_exact_total / count,
        "mean_character_error_rate": cer_total / count,
        "elapsed_ms": round((time.perf_counter() - started) * 1000, 2),
    }
    summary.update(summarize_failures(results))

    return {
        "examples": len(rows),
        "summary": summary,
        "results": results,
    }


def evaluate_suite_rule(
    *,
    entity_csv: str | Path,
    suite_path: str | Path,
    suite_kind: str,
    limit: int | None = None,
) -> dict:
    if suite_kind == "training-jsonl":
        rows = read_jsonl(suite_path)
    else:
        rows = read_evaluation_jsonl(suite_path)

    if limit is not None:
        rows = rows[:limit]

    baseline = RuleBaseline(entity_csv)

    def predict(text: str) -> dict:
        result = baseline.predict(text)
        return {
            "prediction": _prediction_dict_from_rule(result),
            "valid_json": True,
        }

    report = _evaluate_rows(
        rows=rows,
        predict=predict,
        valid_json_default=True,
    )
    report["backend"] = "rule"
    return report


def evaluate_suite_model(
    *,
    model_name: str,
    adapter_path: str | None,
    suite_path: str | Path,
    suite_kind: str,
    limit: int | None = None,
) -> dict:
    if suite_kind == "training-jsonl":
        rows = read_jsonl(suite_path)
    else:
        rows = read_evaluation_jsonl(suite_path)

    if limit is not None:
        rows = rows[:limit]

    backend = TransformersBackend(
        model_name=model_name,
        adapter_path=adapter_path,
    )

    def predict(text: str) -> dict:
        generated = backend.generate(text=text)
        return {
            "prediction": generated.data or {},
            "valid_json": generated.valid_json,
        }

    report = _evaluate_rows(
        rows=rows,
        predict=predict,
        valid_json_default=False,
    )
    report["backend"] = "model"
    report["model_name"] = model_name
    report["adapter_path"] = adapter_path
    return report
