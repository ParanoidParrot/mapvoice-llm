from __future__ import annotations

import csv
import importlib.util
import json
import platform
import sys
from importlib import metadata
from pathlib import Path

from .adapter_registry import AdapterRegistry
from .checkpoints import discover_checkpoints
from .regional_packs import RegionalPackRegistry
from .training_runs import TrainingRunStore


TRAINING_PACKAGES = (
    ("protobuf", "google.protobuf"),
    ("sentencepiece", "sentencepiece"),
    ("datasets", "datasets"),
    ("transformers", "transformers"),
    ("peft", "peft"),
    ("trl", "trl"),
    ("accelerate", "accelerate"),
    ("torch", "torch"),
)


def _package_version(distribution_name: str) -> str | None:
    try:
        return metadata.version(distribution_name)
    except metadata.PackageNotFoundError:
        return None


def dependency_status() -> list[dict]:
    rows = []
    for distribution_name, import_name in TRAINING_PACKAGES:
        installed = importlib.util.find_spec(import_name) is not None
        rows.append({
            "name": distribution_name,
            "import_name": import_name,
            "installed": installed,
            "version": _package_version(distribution_name),
        })
    return rows


def count_json_files(path: Path, prefix: str | None = None) -> int:
    if not path.exists():
        return 0
    if prefix:
        return len(list(path.glob(f"{prefix}*.json")))
    return len(list(path.glob("*.json")))


def count_jsonl_files(path: Path) -> int:
    if not path.exists():
        return 0
    return len(list(path.glob("*.jsonl")))


def csv_row_count(path: Path | None) -> int:
    if path is None or not path.exists():
        return 0
    with path.open(newline="", encoding="utf-8") as handle:
        return sum(1 for _ in csv.DictReader(handle))


def artifact_snapshot(
    *,
    project_root: Path,
    active_entity_csv: Path,
    active_candidate_csv: Path | None,
    adapter_registry: AdapterRegistry,
    training_run_store: TrainingRunStore,
) -> dict:
    experiments_dir = project_root / "outputs" / "experiments"
    improvements_dir = project_root / "outputs" / "improvement_datasets"
    hf_exports_dir = project_root / "outputs" / "hf_exports"
    demo_runs_dir = project_root / "outputs" / "demo_runs"

    hf_exports = []
    if hf_exports_dir.exists():
        hf_exports = sorted(
            str(path.relative_to(project_root))
            for path in hf_exports_dir.iterdir()
            if path.is_dir()
        )

    return {
        "dataset": {
            "entity_rows": csv_row_count(active_entity_csv),
            "candidate_rows": csv_row_count(active_candidate_csv),
            "processed_splits": {
                name: (project_root / "data" / "processed" / f"{name}.jsonl").exists()
                for name in ("train", "validation", "test")
            },
        },
        "training": {
            "training_runs": len(training_run_store.list(limit=1000)),
            "checkpoints": len(discover_checkpoints(project_root / "artifacts")),
        },
        "models": {
            "registered_adapters": len(adapter_registry.list()),
            "active_adapter": (
                adapter_registry.active().get("adapter_id")
                if adapter_registry.active()
                else None
            ),
        },
        "evaluation": {
            "experiments": count_json_files(experiments_dir, "exp_"),
            "improvement_datasets": count_jsonl_files(improvements_dir),
        },
        "demo": {
            "saved_runs": count_json_files(demo_runs_dir, "run_"),
        },
        "publishing": {
            "hf_export_bundles": len(hf_exports),
            "hf_export_paths": hf_exports,
        },
    }


def development_map(snapshot: dict) -> list[dict]:
    dataset = snapshot["dataset"]
    training = snapshot["training"]
    models = snapshot["models"]
    evaluation = snapshot["evaluation"]
    publishing = snapshot["publishing"]

    return [
        {
            "id": "regional-packs",
            "label": "Regional pack framework",
            "status": "implemented",
            "detail": "Pack registry, runtime selection, generic entity schema.",
        },
        {
            "id": "dataset",
            "label": "Dataset pipeline",
            "status": "implemented" if dataset["entity_rows"] else "blocked",
            "detail": (
                f"{dataset['entity_rows']} entities · "
                f"{dataset['candidate_rows']} candidate rows."
            ),
        },
        {
            "id": "normalization",
            "label": "Rule baseline",
            "status": "implemented",
            "detail": "Normalization, lexicon lookup and native-script output.",
        },
        {
            "id": "training",
            "label": "LoRA training",
            "status": "ready-to-run",
            "detail": (
                f"{training['training_runs']} recorded training runs · "
                f"{training['checkpoints']} discovered checkpoints."
            ),
        },
        {
            "id": "evaluation",
            "label": "Evaluation & failures",
            "status": "implemented",
            "detail": (
                f"{evaluation['experiments']} saved experiments · "
                f"{evaluation['improvement_datasets']} improvement exports."
            ),
        },
        {
            "id": "adapters",
            "label": "Adapter lifecycle",
            "status": "implemented",
            "detail": (
                f"{models['registered_adapters']} registered · "
                f"active: {models['active_adapter'] or 'none'}."
            ),
        },
        {
            "id": "tts",
            "label": "TTS integration",
            "status": "optional",
            "detail": "Sarvam provider abstraction and audio comparison.",
        },
        {
            "id": "publishing",
            "label": "Model hosting export",
            "status": "implemented",
            "detail": (
                f"{publishing['hf_export_bundles']} offline export bundles."
            ),
        },
    ]


def project_status(
    *,
    project_root: Path,
    active_pack: dict,
    active_entity_csv: Path,
    active_candidate_csv: Path | None,
    adapter_registry: AdapterRegistry,
    training_run_store: TrainingRunStore,
    tts_status: dict,
    model_name: str | None,
) -> dict:
    snapshot = artifact_snapshot(
        project_root=project_root,
        active_entity_csv=active_entity_csv,
        active_candidate_csv=active_candidate_csv,
        adapter_registry=adapter_registry,
        training_run_store=training_run_store,
    )
    dependencies = dependency_status()

    active_pack_id = active_pack.get("pack_id")
    pack_manifest = (
        project_root / "data" / "processed" / "packs" / str(active_pack_id) / "manifest.json"
    )
    snapshot["training"]["pack_dataset_manifest_exists"] = pack_manifest.exists()
    snapshot["training"]["pack_dataset_manifest"] = (
        str(pack_manifest.relative_to(project_root)) if pack_manifest.exists() else None
    )

    return {
        "project": "MapVoice-LLM",
        "version": "1.9.0",
        "runtime": {
            "python": sys.version.split()[0],
            "python_executable": sys.executable,
            "platform": platform.platform(),
            "recommended_python": "3.12",
        },
        "active_pack": active_pack,
        "base_model": model_name,
        "dependencies": dependencies,
        "dependency_summary": {
            "installed": sum(row["installed"] for row in dependencies),
            "total": len(dependencies),
            "all_installed": all(row["installed"] for row in dependencies),
        },
        "artifacts": snapshot,
        "tts": tts_status,
        "development_map": development_map(snapshot),
    }
