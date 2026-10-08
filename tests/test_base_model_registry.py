from pathlib import Path

from mapvoice_llm.base_model_registry import BaseModelRegistry


def test_base_model_registry_has_reference_and_open_comparison():
    root = Path(__file__).resolve().parents[1]
    registry = BaseModelRegistry(
        root / "configs" / "base_models.json"
    )

    assert registry.reference().model_key == "sarvam-1"
    keys = {model.model_key for model in registry.list()}
    assert "qwen2.5-1.5b-instruct" in keys
    assert "gemma3-1b-it" in keys
