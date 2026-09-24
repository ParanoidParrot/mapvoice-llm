from mapvoice_llm.prompts import build_prompt, format_sft_example


def test_prompt_contains_navigation_text():
    prompt = build_prompt(text="Turn left towards Jayanagar.")
    assert "Turn left towards Jayanagar." in prompt
    assert "Bengaluru" in prompt


def test_sft_record_contains_target():
    record = {
        "input": {
            "city": "Bengaluru",
            "region_language": "Kannada",
            "navigation_language": "English",
            "text": "Continue towards Jayanagar.",
        },
        "target": {
            "place_name": "Jayanagar",
            "place_name_kn": "ಜಯನಗರ",
            "entity_type": "locality",
            "language_origin": "Kannada",
            "pronunciation_form": "ಜಯನಗರ",
        },
    }

    formatted = format_sft_example(record)
    assert formatted["prompt"] in formatted["text"]
    assert "ಜಯನಗರ" in formatted["completion"]
