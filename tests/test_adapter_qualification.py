from mapvoice_llm.adapter_qualification import qualify_adapter


POLICY = {
    "prototype": {
        "minimum_test_examples": 16,
        "minimum_valid_json_rate": 0.8,
        "minimum_spoken_exact_delta": 0.0,
        "maximum_cer_delta": 0.0,
        "maximum_entity_exact_regression": 0.05,
    },
    "publishable": {
        "allowed_dataset_policies": [
            "reviewed",
            "verified",
            "pronunciation-verified",
        ],
        "minimum_test_examples": 24,
        "minimum_valid_json_rate": 0.95,
        "minimum_spoken_exact_delta": 0.05,
        "maximum_cer_delta": -0.02,
        "maximum_entity_exact_regression": 0.0,
    },
}


def report(spoken, cer, entity, valid=1.0, examples=24):
    return {
        "examples": examples,
        "summary": {
            "valid_json_rate": valid,
            "spoken_form_exact_match": spoken,
            "mean_character_error_rate": cer,
            "entity_exact_match": entity,
        },
    }


def test_labeled_adapter_can_be_prototype_but_not_publishable():
    result = qualify_adapter(
        base_report=report(0.4, 0.4, 0.6),
        adapter_report=report(0.6, 0.2, 0.7),
        dataset_policy="labeled",
        policy=POLICY,
    )

    assert result["prototype"]["passed"]
    assert not result["publishable"]["passed"]
    assert not result["publishable"]["checks"]["dataset_policy_allowed"]
