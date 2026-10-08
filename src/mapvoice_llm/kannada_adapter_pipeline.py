from __future__ import annotations

import json
import subprocess
import sys
import time
import uuid
from pathlib import Path

from .adapter_qualification import (
    load_qualification_policy,
    qualify_adapter,
)
from .adapter_registry import AdapterRegistry
from .base_model_registry import BaseModelRegistry
from .evaluator import evaluate_model
from .experiment_store import ExperimentStore
from .hf_export import (
    adapter_manifest,
    write_export_bundle,
)
from .pack_context import load_pack_context
from .pack_dataset import build_pack_dataset
from .pack_evaluation import build_pack_evaluation
from .training_plan import build_training_plan
from .training_profiles import TrainingProfileRegistry


PACK_ID = "blr-kn"


def _result_dir(
    project_root: Path,
    lifecycle_id: str,
) -> Path:
    path = (
        project_root
        / "outputs"
        / "adapter_lifecycle"
        / lifecycle_id
    )
    path.mkdir(parents=True, exist_ok=True)
    return path


def prepare_kannada_adapter(
    *,
    project_root: str | Path,
    profile_id: str = "local-mac",
    dataset_policy: str = "labeled",
    adapter_version: str = "v1",
    model_name: str | None = None,
) -> dict:
    project_root = Path(project_root)
    context = load_pack_context(
        project_root,
        PACK_ID,
    )

    dataset = build_pack_dataset(
        project_root=project_root,
        pack=context.pack,
        entity_repository=context.entity_repository,
        policy_id=dataset_policy,
    )

    evaluation = build_pack_evaluation(
        project_root=project_root,
        pack=context.pack,
        entities=context.entity_repository.list(),
    )

    profile = TrainingProfileRegistry(
        project_root
        / "configs"
        / "training_profiles.json"
    ).get(profile_id)

    plan = build_training_plan(
        project_root=project_root,
        pack=context.pack,
        profile=profile,
        version=adapter_version,
        model_name=model_name,
        dataset_policy=dataset_policy,
    )

    return {
        "pack_id": PACK_ID,
        "dataset": dataset.to_dict(),
        "evaluation": evaluation,
        "training_plan": plan.to_dict(),
        "corpus_warning": (
            "This is currently a prototype corpus. "
            "The 'labeled' policy is not equivalent to "
            "reviewed/verified publication-quality data."
            if dataset_policy == "labeled"
            else None
        ),
    }


def _training_args(
    *,
    project_root: Path,
    plan: dict,
    dataset_policy: str,
) -> list[str]:
    return [
        sys.executable,
        str(
            project_root
            / "training"
            / "train_lora.py"
        ),
        "--model-name",
        plan["model_name"],
        "--train-file",
        plan["train_file"],
        "--validation-file",
        plan["validation_file"],
        "--output-dir",
        plan["output_dir"],
        "--quantization",
        plan["quantization"],
        "--adapter-id",
        plan["adapter_id"],
        "--register-adapter",
        "--epochs",
        str(plan["epochs"]),
        "--learning-rate",
        str(plan["learning_rate"]),
        "--batch-size",
        str(plan["batch_size"]),
        "--grad-accum",
        str(plan["gradient_accumulation_steps"]),
        "--pack-id",
        PACK_ID,
        "--dataset-policy",
        dataset_policy,
    ]


def run_training(
    *,
    project_root: Path,
    plan: dict,
    dataset_policy: str,
) -> dict:
    args = _training_args(
        project_root=project_root,
        plan=plan,
        dataset_policy=dataset_policy,
    )

    proc = subprocess.run(
        args,
        cwd=project_root,
        text=True,
    )

    if proc.returncode != 0:
        raise RuntimeError(
            f"LoRA training exited with code "
            f"{proc.returncode}"
        )

    return {
        "returncode": proc.returncode,
        "adapter_id": plan["adapter_id"],
        "output_dir": plan["output_dir"],
    }


def evaluate_kannada_adapter(
    *,
    project_root: str | Path,
    adapter_id: str,
    dataset_policy: str = "labeled",
    limit: int | None = None,
    promote_if_passes: bool = False,
    export_bundle: bool = False,
) -> dict:
    project_root = Path(project_root)
    context = load_pack_context(
        project_root,
        PACK_ID,
    )

    registry = AdapterRegistry(
        project_root
        / "configs"
        / "adapter_registry.json"
    )
    adapter = registry.get(adapter_id)
    if adapter is None:
        raise KeyError(
            f"Adapter is not registered: {adapter_id}"
        )

    test_file = (
        project_root
        / "data"
        / "processed"
        / "packs"
        / PACK_ID
    )
    if dataset_policy != "labeled":
        test_file = (
            test_file / dataset_policy
        )
    test_file = test_file / "test.jsonl"

    if not test_file.exists():
        raise FileNotFoundError(test_file)

    base_model = adapter["base_model"]
    base_report = evaluate_model(
        model_name=base_model,
        adapter_path=None,
        test_file=test_file,
        limit=limit,
    )
    adapter_report = evaluate_model(
        model_name=base_model,
        adapter_path=adapter["adapter_path"],
        test_file=test_file,
        limit=limit,
    )

    experiment_store = ExperimentStore(
        project_root
        / "outputs"
        / "experiments"
    )

    base_experiment = experiment_store.save({
        **base_report,
        "suite_id": "pack-entity-held-out",
        "suite_label": "BLR-KN entity-held-out",
        "pack_id": PACK_ID,
        "dataset_policy": dataset_policy,
        "role": "base-for-adapter-qualification",
    })

    adapter_experiment = experiment_store.save({
        **adapter_report,
        "suite_id": "pack-entity-held-out",
        "suite_label": "BLR-KN entity-held-out",
        "pack_id": PACK_ID,
        "dataset_policy": dataset_policy,
        "role": "adapter-qualification",
        "adapter_id": adapter_id,
    })

    qualification_policy = (
        load_qualification_policy(
            project_root
            / "configs"
            / "adapter_qualification.json"
        )
    )
    qualification = qualify_adapter(
        base_report=base_report,
        adapter_report=adapter_report,
        dataset_policy=dataset_policy,
        policy=qualification_policy,
    )

    registry.register({
        **adapter,
        "pack_id": PACK_ID,
        "dataset_policy": dataset_policy,
        "qualification": qualification,
        "base_experiment_id": (
            base_experiment["experiment_id"]
        ),
        "adapter_experiment_id": (
            adapter_experiment["experiment_id"]
        ),
        "evaluation_summary": (
            adapter_report["summary"]
        ),
    })

    promoted = False
    if (
        promote_if_passes
        and qualification["prototype"]["passed"]
    ):
        registry.promote(adapter_id)
        promoted = True

    export_path = None
    if export_bundle:
        model_registry = BaseModelRegistry(
            project_root
            / "configs"
            / "base_models.json"
        )
        base_metadata = next(
            (
                model
                for model in model_registry.list()
                if model.hf_model_id == base_model
            ),
            None,
        )

        refreshed = registry.get(adapter_id) or adapter
        manifest = adapter_manifest(
            adapter=refreshed,
            pack=context.pack.to_dict(),
            metrics=adapter_report["summary"],
            license_name=(
                "other"
                if base_metadata is None
                else (
                    "apache-2.0"
                    if base_metadata.license_family
                    == "Apache-2.0"
                    else "other"
                )
            ),
        )
        manifest["qualification"] = qualification
        manifest["dataset_policy"] = dataset_policy
        manifest["base_model_metadata"] = (
            base_metadata.to_dict()
            if base_metadata
            else None
        )

        export_path = (
            project_root
            / "outputs"
            / "hf_exports"
            / adapter_id
        )
        write_export_bundle(
            output_dir=export_path,
            manifest=manifest,
        )

    return {
        "adapter_id": adapter_id,
        "base_model": base_model,
        "dataset_policy": dataset_policy,
        "test_file": str(
            test_file.relative_to(project_root)
        ),
        "base_experiment_id": (
            base_experiment["experiment_id"]
        ),
        "adapter_experiment_id": (
            adapter_experiment["experiment_id"]
        ),
        "base_summary": base_report["summary"],
        "adapter_summary": (
            adapter_report["summary"]
        ),
        "qualification": qualification,
        "promoted": promoted,
        "export_path": (
            str(export_path.relative_to(project_root))
            if export_path
            else None
        ),
    }


def lifecycle_status(
    *,
    project_root: str | Path,
    adapter_id: str = "mapvoice-blr-kn-v1",
) -> dict:
    project_root = Path(project_root)
    registry = AdapterRegistry(
        project_root
        / "configs"
        / "adapter_registry.json"
    )
    adapter = registry.get(adapter_id)
    active = registry.active()

    artifact_dir = (
        project_root
        / "artifacts"
        / adapter_id
    )

    return {
        "pack_id": PACK_ID,
        "adapter_id": adapter_id,
        "registered": adapter is not None,
        "registry_record": adapter,
        "artifact_dir_exists": artifact_dir.exists(),
        "adapter_config_exists": (
            artifact_dir
            / "adapter_config.json"
        ).exists(),
        "active": bool(
            active
            and active.get("adapter_id")
            == adapter_id
        ),
    }
