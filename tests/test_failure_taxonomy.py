from mapvoice_llm.failure_taxonomy import classify_failure


def codes(failures):
    return {failure.code for failure in failures}


def test_wrong_entity_and_spoken_form():
    failures = classify_failure(
        target={
            "place_name": "Jayanagar",
            "place_name_kn": "ಜಯನಗರ",
            "spoken_form": "ಜಯನಗರ",
        },
        prediction={
            "place_name": "Rajajinagar",
            "place_name_kn": "ರಾಜಾಜಿನಗರ",
            "spoken_form": "ರಾಜಾಜಿನಗರ",
        },
        cer=0.8,
    )

    result = codes(failures)

    assert "wrong_entity" in result
    assert "wrong_kannada" in result
    assert "wrong_spoken_form" in result
    assert "high_cer" in result


def test_invalid_json():
    failures = classify_failure(
        target={"place_name": "X"},
        prediction={},
        valid_json=False,
    )

    assert "invalid_json" in codes(failures)
