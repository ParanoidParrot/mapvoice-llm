from mapvoice_llm.demo_runs import DemoRunStore


def test_demo_run_round_trip(tmp_path):
    store = DemoRunStore(tmp_path)
    created = store.create({"original_text": "hello"})

    loaded = store.get(created["run_id"])

    assert loaded is not None
    assert loaded["original_text"] == "hello"
    assert store.list(limit=10)[0]["run_id"] == created["run_id"]
