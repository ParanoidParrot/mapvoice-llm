from evaluation.reporting import summarize_predictions


def test_summary():
    rows = [
        {
            "valid_json": True,
            "target": {
                "place_name": "Jayanagar",
                "spoken_form": "ಜಯನಗರ",
                "entity_type": "locality",
            },
            "prediction": {
                "place_name": "Jayanagar",
                "spoken_form": "ಜಯನಗರ",
            },
        }
    ]

    summary = summarize_predictions(rows)
    assert summary["examples"] == 1
    assert summary["valid_json_rate"] == 1.0
    assert summary["entity_exact_match"] == 1.0
    assert summary["spoken_form_exact_match"] == 1.0
    assert summary["mean_character_error_rate"] == 0.0
