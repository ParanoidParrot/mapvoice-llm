from __future__ import annotations

import json
import time
import uuid
from pathlib import Path

from .base_model_registry import BaseModelDefinition
from .evaluator import evaluate_model
from .tokenizer_benchmark import tokenizer_diagnostics


def resolve_pack_test_file(
    *,
    project_root: str | Path,
    pack_id: str,
    policy_id: str = "labeled",
) -> Path:
    project_root = Path(project_root)

    if policy_id == "labeled":
        legacy = (
            project_root
            / "data"
            / "processed"
            / "packs"
            / pack_id
            / "test.jsonl"
        )
        if legacy.exists():
            return legacy

    return (
        project_root
        / "data"
        / "processed"
        / "packs"
        / pack_id
        / policy_id
        / "test.jsonl"
    )


def benchmark_plan(
    *,
    project_root: str | Path,
    pack_id: str,
    models: list[BaseModelDefinition],
    policy_id: str = "labeled",
    limit: int | None = None,
) -> dict:
    test_file = resolve_pack_test_file(
        project_root=project_root,
        pack_id=pack_id,
        policy_id=policy_id,
    )

    return {
        "pack_id": pack_id,
        "policy_id": policy_id,
        "test_file": str(test_file),
        "limit": limit,
        "models": [model.to_dict() for model in models],
    }


def _ordering_key(row: dict) -> tuple:
    summary = row.get("evaluation", {}).get("summary", {})
    # Transparent task ordering, not a fabricated universal score:
    # spoken exact desc, CER asc, entity exact desc, valid JSON desc.
    return (
        -(summary.get("spoken_form_exact_match") or 0),
        summary.get("mean_character_error_rate")
        if summary.get("mean_character_error_rate") is not None
        else 999,
        -(summary.get("entity_exact_match") or 0),
        -(summary.get("valid_json_rate") or 0),
    )


def run_base_model_benchmark(
    *,
    project_root: str | Path,
    pack_id: str,
    models: list[BaseModelDefinition],
    policy_id: str = "labeled",
    limit: int | None = None,
    tokenizer_only: bool = False,
) -> dict:
    project_root = Path(project_root)
    test_file = resolve_pack_test_file(
        project_root=project_root,
        pack_id=pack_id,
        policy_id=policy_id,
    )

    if not test_file.exists():
        raise FileNotFoundError(
            f"Pack test split not found: {test_file}. "
            f"Build it first with scripts/build_pack_dataset.py."
        )

    rows = []

    for model in models:
        record = {
            "model": model.to_dict(),
            "status": "running",
            "tokenizer": None,
            "evaluation": None,
            "error": None,
        }

        try:
            record["tokenizer"] = tokenizer_diagnostics(
                model_name=model.hf_model_id,
                test_file=test_file,
                limit=limit,
            )

            if not tokenizer_only:
                record["evaluation"] = evaluate_model(
                    model_name=model.hf_model_id,
                    adapter_path=None,
                    test_file=test_file,
                    limit=limit,
                )

            record["status"] = "completed"
        except Exception as exc:
            record["status"] = "failed"
            record["error"] = (
                f"{type(exc).__name__}: {exc}"
            )

        rows.append(record)

    completed = [
        row
        for row in rows
        if row["status"] == "completed"
        and row.get("evaluation")
    ]
    completed.sort(key=_ordering_key)

    benchmark_id = (
        "basebench_"
        + uuid.uuid4().hex[:12]
    )
    result = {
        "benchmark_id": benchmark_id,
        "created_at_epoch": time.time(),
        "pack_id": pack_id,
        "policy_id": policy_id,
        "test_file": str(test_file.relative_to(project_root)),
        "limit": limit,
        "tokenizer_only": tokenizer_only,
        "results": rows,
        "task_ordering": [
            row["model"]["model_key"]
            for row in completed
        ],
        "ordering_definition": (
            "spoken_form_exact_match desc, "
            "mean_character_error_rate asc, "
            "entity_exact_match desc, "
            "valid_json_rate desc"
        ),
    }

    output_dir = (
        project_root
        / "outputs"
        / "base_model_benchmarks"
    )
    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    output = output_dir / f"{benchmark_id}.json"
    output.write_text(
        json.dumps(
            result,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    result["output"] = str(
        output.relative_to(project_root)
    )

    return result
