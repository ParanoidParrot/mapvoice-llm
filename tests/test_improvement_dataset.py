from mapvoice_llm.improvement_dataset import build_improvement_rows


def test_only_failed_rows_are_exported():
    experiment = {
        "suite_id": "hard",
        "backend": "rule",
        "results": [
            {
                "example_id": "ok",
                "failures": [],
            },
            {
                "example_id": "bad",
                "text": "Continue towards X",
                "failures": [{"code": "wrong_entity"}],
                "target": {},
                "prediction": {},
                "metrics": {},
            },
        ],
    }

    rows = build_improvement_rows(experiment)

    assert len(rows) == 1
    assert rows[0]["example_id"] == "bad"
