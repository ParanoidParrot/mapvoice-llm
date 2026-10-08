import csv

from mapvoice_llm.baseline import RuleBaseline
from mapvoice_llm.pack_schema import GENERIC_ENTITY_FIELDS


def test_generic_regional_baseline(tmp_path):
    path = tmp_path / "entities.csv"

    with path.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=GENERIC_ENTITY_FIELDS,
        )
        writer.writeheader()
        writer.writerow({
            "entity_id": "x1",
            "latin_name": "Example",
            "native_name": "NativeScript",
            "entity_type": "locality",
            "city": "City",
            "language": "Language",
            "language_code": "xx",
            "alternate_spellings": "",
            "morphemes": "",
            "suffix": "",
            "verification_status": "reviewed",
            "pronunciation_verified": "false",
            "source_name": "",
            "source_url": "",
            "source_type": "",
            "reviewer": "",
            "notes": "",
        })

    result = RuleBaseline(path).predict(
        "Continue towards Example."
    )

    assert result.detected_entity == "Example"
    assert result.entity_native == "NativeScript"
    assert result.spoken_form == "NativeScript"
