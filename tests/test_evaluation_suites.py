from mapvoice_llm.evaluation_suites import EvaluationSuiteRegistry


def test_suite_registry(tmp_path):
    registry = EvaluationSuiteRegistry(tmp_path)
    suites = registry.list()

    ids = {suite["id"] for suite in suites}

    assert "entity-held-out" in ids
    assert "morphological-hard" in ids
    assert registry.get("lexicon-known")["label"] == "Lexicon-known"
