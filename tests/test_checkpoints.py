from mapvoice_llm.checkpoints import discover_checkpoints


def test_checkpoint_discovery(tmp_path):
    checkpoint = tmp_path / "model" / "checkpoint-100"
    checkpoint.mkdir(parents=True)
    (checkpoint / "adapter_config.json").write_text("{}")
    (checkpoint / "adapter_model.safetensors").write_bytes(b"x")

    rows = discover_checkpoints(tmp_path)

    assert len(rows) == 1
    assert rows[0]["has_adapter_config"] is True
    assert rows[0]["has_adapter_weights"] is True
