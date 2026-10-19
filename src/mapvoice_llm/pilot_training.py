from __future__ import annotations

import shlex
from pathlib import Path

from .pilot_builder import pilot_status
from .pilot_profiles import PilotProfile
from .training_profiles import TrainingProfile


def build_pilot_training_plan(
    *,
    project_root: str | Path,
    pack,
    pilot_profile: PilotProfile,
    training_profile: TrainingProfile,
    model_name: str,
    adapter_version: str = "v1",
) -> dict:
    project_root = Path(project_root)

    status = pilot_status(
        project_root=project_root,
        pack_id=pack.pack_id,
        profile=pilot_profile,
    )

    if not status["ready"]:
        return {
            **status,
            "plan_ready": False,
        }

    pilot_dir = (
        Path("data")
        / "pilots"
        / pack.pack_id
    )

    adapter_id = (
        f"mapvoice-{pack.pack_id}-pilot-{adapter_version}"
    )

    output_dir = (
        Path("artifacts")
        / adapter_id
    )

    args = [
        "python",
        "training/train_lora.py",
        "--model-name",
        model_name,
        "--train-file",
        str(
            pilot_dir
            / "train.jsonl"
        ),
        "--validation-file",
        str(
            pilot_dir
            / "validation.jsonl"
        ),
        "--output-dir",
        str(output_dir),
        "--quantization",
        training_profile.quantization,
        "--adapter-id",
        adapter_id,
        "--register-adapter",
        "--pack-id",
        pack.pack_id,
        "--dataset-policy",
        "pilot-reviewed",
        "--epochs",
        str(training_profile.epochs),
        "--learning-rate",
        str(training_profile.learning_rate),
        "--batch-size",
        str(training_profile.batch_size),
        "--grad-accum",
        str(
            training_profile.gradient_accumulation_steps
        ),
    ]

    return {
        **status,
        "plan_ready": True,
        "adapter_id": adapter_id,
        "model_name": model_name,
        "training_profile": (
            training_profile.profile_id
        ),
        "command": " \\\n  ".join(
            shlex.quote(item)
            for item in args
        ),
    }
