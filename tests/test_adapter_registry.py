from mapvoice_llm.adapter_registry import AdapterRegistry


def test_register_and_promote(tmp_path):
    registry = AdapterRegistry(tmp_path / "registry.json")

    registry.register({
        "adapter_id": "a1",
        "adapter_path": "/tmp/a1",
        "base_model": "base",
    })
    registry.register({
        "adapter_id": "a2",
        "adapter_path": "/tmp/a2",
        "base_model": "base",
    })

    promoted = registry.promote("a2")

    assert promoted["adapter_id"] == "a2"
    assert registry.active()["adapter_id"] == "a2"
    assert len(registry.list()) == 2
