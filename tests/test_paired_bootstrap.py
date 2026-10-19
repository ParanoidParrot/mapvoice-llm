from mapvoice_llm.paired_bootstrap import paired_bootstrap_delta


def test_bootstrap_detects_consistent_improvement():
    result = paired_bootstrap_delta(
        [0, 0, 1, 0, 1],
        [1, 1, 1, 1, 1],
        iterations=200,
        seed=42,
    )

    assert result["observed_delta"] > 0
    assert result["probability_second_better"] > 0.9
