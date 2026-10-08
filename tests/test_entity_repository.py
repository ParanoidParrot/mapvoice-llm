import csv

from mapvoice_llm.entity_repository import RegionalEntityRepository
from mapvoice_llm.pack_schema import GENERIC_ENTITY_FIELDS


def test_generic_entity_repository(tmp_path):
    path = tmp_path / "entities.csv"

    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=GENERIC_ENTITY_FIELDS)
        writer.writeheader()
        writer.writerow({
            "entity_id": "x",
            "latin_name": "Example",
            "native_name": "ಉದಾಹರಣೆ",
            "entity_type": "locality",
            "city": "Bengaluru",
            "language": "Kannada",
            "language_code": "kn",
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

    rows = RegionalEntityRepository(path).list()

    assert len(rows) == 1
    assert rows[0].latin_name == "Example"
    assert rows[0].native_name == "ಉದಾಹರಣೆ"
