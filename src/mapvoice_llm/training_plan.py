from __future__ import annotations
import shlex
from dataclasses import dataclass, asdict
from pathlib import Path
from .artifact_naming import default_adapter_id
from .regional_packs import RegionalPack
from .training_profiles import TrainingProfile

@dataclass(frozen=True)
class TrainingPlan:
    pack_id: str
    dataset_policy: str
    profile_id: str
    model_name: str
    adapter_id: str
    train_file: str
    validation_file: str
    output_dir: str
    quantization: str
    epochs: int
    learning_rate: float
    batch_size: int
    gradient_accumulation_steps: int
    command: str
    warnings: list[str]
    def to_dict(self) -> dict:
        return asdict(self)

def build_training_plan(
    *,
    project_root: str | Path,
    pack: RegionalPack,
    profile: TrainingProfile,
    version: str = "v1",
    model_name: str | None = None,
    dataset_policy: str = "labeled",
) -> TrainingPlan:
    chosen_model = model_name or pack.default_base_model or "sarvamai/sarvam-1"
    adapter_id = default_adapter_id(pack_id=pack.pack_id, version=version)
    processed_dir = Path("data") / "processed" / "packs" / pack.pack_id
    if dataset_policy != "labeled":
        processed_dir = processed_dir / dataset_policy
    train_file = processed_dir / "train.jsonl"
    validation_file = processed_dir / "validation.jsonl"
    output_dir = Path("artifacts") / adapter_id
    args = [
        "python", "training/train_lora.py",
        "--model-name", chosen_model,
        "--train-file", str(train_file),
        "--validation-file", str(validation_file),
        "--output-dir", str(output_dir),
        "--quantization", profile.quantization,
        "--adapter-id", adapter_id,
        "--register-adapter",
        "--pack-id", pack.pack_id,
        "--dataset-policy", dataset_policy,
        "--epochs", str(profile.epochs),
        "--learning-rate", str(profile.learning_rate),
        "--batch-size", str(profile.batch_size),
        "--grad-accum", str(profile.gradient_accumulation_steps),
    ]
    warnings=[]
    if profile.quantization == "4bit":
        warnings.append("4-bit QLoRA requires a compatible CUDA/bitsandbytes environment.")
    if profile.recommended_device == "mps":
        warnings.append("Apple MPS is useful for development, but model size and unified memory can make full training impractical.")
    return TrainingPlan(
        pack_id=pack.pack_id, dataset_policy=dataset_policy, profile_id=profile.profile_id, model_name=chosen_model,
        adapter_id=adapter_id, train_file=str(train_file), validation_file=str(validation_file),
        output_dir=str(output_dir), quantization=profile.quantization, epochs=profile.epochs,
        learning_rate=profile.learning_rate, batch_size=profile.batch_size,
        gradient_accumulation_steps=profile.gradient_accumulation_steps,
        command=" \\\n  ".join(shlex.quote(x) for x in args), warnings=warnings,
    )
