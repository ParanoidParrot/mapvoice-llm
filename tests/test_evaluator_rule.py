import csv
import json

from mapvoice_llm.evaluator import evaluate_rule


def test_rule_evaluator(tmp_path):
    entities = tmp_path / "entities.csv"
    fields = [
        "entity_id","english_name","kannada_name","entity_type",
        "city","language","alternate_spellings","morphemes",
        "suffix","verification_status","pronunciation_verified",
        "source_name","source_url","source_type","reviewer","notes",
    ]

    with entities.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerow({
            "entity_id": "x",
            "english_name": "Jayanagar",
            "kannada_name": "ಜಯನಗರ",
            "entity_type": "locality",
            "city": "Bengaluru",
            "language": "Kannada",
            "alternate_spellings": "",
            "morphemes": "",
            "suffix": "nagar",
            "verification_status": "reviewed",
            "pronunciation_verified": "false",
            "source_name": "",
            "source_url": "",
            "source_type": "",
            "reviewer": "",
            "notes": "",
        })

    test_file = tmp_path / "test.jsonl"
    row = {
        "example_id": "x_0",
        "entity_id": "x",
        "input": {
            "city": "Bengaluru",
            "region_language": "Kannada",
            "navigation_language": "English",
            "text": "Continue towards Jayanagar.",
        },
        "target": {
            "place_name": "Jayanagar",
            "spoken_form": "ಜಯನಗರ",
            "entity_type": "locality",
        },
    }

    test_file.write_text(
        json.dumps(row, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    report = evaluate_rule(
        entity_csv=entities,
        test_file=test_file,
    )

    assert report["summary"]["entity_exact_match"] == 1.0
    assert report["summary"]["spoken_form_exact_match"] == 1.0
