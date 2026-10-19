from pathlib import Path

from mapvoice_llm.benchmark_protocol import BenchmarkProtocol


def test_protocol_is_versioned_and_has_primary_metrics():
    root = Path(__file__).resolve().parents[1]
    protocol = BenchmarkProtocol.load(
        root / "configs" / "benchmark_protocol.json"
    )

    assert protocol.protocol_id == "mapvoice-benchmark-v1"
    assert "spoken_form_exact_match" in protocol.primary_metrics
    assert protocol.paired_bootstrap["enabled"]
