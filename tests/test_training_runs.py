from mapvoice_llm.training_runs import TrainingRunStore


def test_training_run_lifecycle(tmp_path):
    store = TrainingRunStore(tmp_path)

    run = store.start({"model_name": "base"})
    assert run["status"] == "running"

    finished = store.finish(
        run["run_id"],
        output_dir="/tmp/output",
        metrics={"loss": 1.23},
    )

    assert finished["status"] == "completed"
    assert finished["metrics"]["loss"] == 1.23
    assert store.list()[0]["run_id"] == run["run_id"]
