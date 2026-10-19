from pathlib import Path

from mapvoice_llm.source_registry import SourceRegistry


def test_koel_reference_source_registered():
    root = Path(__file__).resolve().parents[1]
    source = SourceRegistry(
        root / "configs/source_registry.json"
    ).get("koel-locality-benchmark")

    assert source.source_type == "huggingface-dataset"
    assert "chn-ta" in source.allowed_pack_ids
