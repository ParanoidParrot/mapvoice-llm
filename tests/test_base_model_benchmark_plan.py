from pathlib import Path

from mapvoice_llm.base_model_benchmark import benchmark_plan
from mapvoice_llm.base_model_registry import BaseModelRegistry


def test_benchmark_plan_uses_same_pack_test_split():
    root = Path(__file__).resolve().parents[1]
    registry = BaseModelRegistry(
        root / "configs" / "base_models.json"
    )

    plan = benchmark_plan(
        project_root=root,
        pack_id="blr-kn",
        models=[registry.reference()],
        policy_id="labeled",
        limit=24,
    )

    assert plan["pack_id"] == "blr-kn"
    assert plan["limit"] == 24
    assert plan["test_file"].endswith(
        "data/processed/packs/blr-kn/test.jsonl"
    )
