from mapvoice_llm.experiment_store import ExperimentStore


def test_experiment_store_round_trip(tmp_path):
    store = ExperimentStore(tmp_path)
    created = store.save({
        "backend": "rule",
        "summary": {"entity_exact_match": 1.0},
    })

    loaded = store.get(created["experiment_id"])

    assert loaded is not None
    assert loaded["backend"] == "rule"
    assert store.list(limit=10)[0]["experiment_id"] == created["experiment_id"]
