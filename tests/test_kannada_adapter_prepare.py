from pathlib import Path

from mapvoice_llm.kannada_adapter_pipeline import prepare_kannada_adapter


def test_kannada_adapter_prepare_builds_v1_plan():
    root = Path(__file__).resolve().parents[1]

    result = prepare_kannada_adapter(
        project_root=root,
        profile_id="local-mac",
        dataset_policy="labeled",
        adapter_version="v1",
    )

    plan = result["training_plan"]
    assert plan["adapter_id"] == "mapvoice-blr-kn-v1"
    assert plan["pack_id"] == "blr-kn"
    assert plan["dataset_policy"] == "labeled"
    assert result["dataset"]["total_examples"] == 160
