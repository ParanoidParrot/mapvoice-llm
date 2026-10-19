from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from mapvoice_llm.base_model_registry import BaseModelRegistry
from mapvoice_llm.pack_context import load_pack_context
from mapvoice_llm.pilot_profiles import PilotProfileRegistry
from mapvoice_llm.pilot_training import build_pilot_training_plan
from mapvoice_llm.training_profiles import TrainingProfileRegistry


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pack-id", required=True)
    parser.add_argument("--training-profile", default="local-mac")
    parser.add_argument("--base-model", default="sarvam-1")
    parser.add_argument("--adapter-version", default="v1")
    args = parser.parse_args()

    context = load_pack_context(PROJECT_ROOT, args.pack_id)

    pilot_profile = PilotProfileRegistry(
        PROJECT_ROOT / "configs" / "pilot_profiles.json"
    ).get(args.pack_id)

    training_profile = TrainingProfileRegistry(
        PROJECT_ROOT / "configs" / "training_profiles.json"
    ).get(args.training_profile)

    model = BaseModelRegistry(
        PROJECT_ROOT / "configs" / "base_models.json"
    ).get(args.base_model)

    result = build_pilot_training_plan(
        project_root=PROJECT_ROOT,
        pack=context.pack,
        pilot_profile=pilot_profile,
        training_profile=training_profile,
        model_name=model.hf_model_id,
        adapter_version=args.adapter_version,
    )

    print(json.dumps(
        result,
        ensure_ascii=False,
        indent=2,
    ))


if __name__ == "__main__":
    main()
