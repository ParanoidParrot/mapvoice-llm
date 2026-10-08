import csv

from mapvoice_llm.adapter_registry import AdapterRegistry
from mapvoice_llm.project_status import project_status
from mapvoice_llm.training_runs import TrainingRunStore


def test_project_status_snapshot(tmp_path):
    entities = tmp_path / "entities.csv"
    with entities.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["entity_id", "english_name"],
        )
        writer.writeheader()
        writer.writerow({"entity_id": "1", "english_name": "Example"})

    candidates = tmp_path / "candidates.csv"
    with candidates.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["candidate_id", "annotation_status"],
        )
        writer.writeheader()
        writer.writerow({"candidate_id": "c1", "annotation_status": "candidate"})

    status = project_status(
        project_root=tmp_path,
        active_pack={
            "pack_id": "x-y",
            "city": "City",
            "region_language": "Language",
        },
        active_entity_csv=entities,
        active_candidate_csv=candidates,
        adapter_registry=AdapterRegistry(tmp_path / "adapter_registry.json"),
        training_run_store=TrainingRunStore(tmp_path / "training_runs"),
        tts_status={"enabled": False, "provider": "disabled", "available": False},
        model_name="base/model",
    )

    assert status["project"] == "MapVoice-LLM"
    assert status["artifacts"]["dataset"]["entity_rows"] == 1
    assert status["artifacts"]["dataset"]["candidate_rows"] == 1
    assert status["development_map"]
