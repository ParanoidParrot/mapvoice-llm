import csv
import json

from mapvoice_llm.entity_repository import RegionalEntityRepository
from mapvoice_llm.pack_dataset import build_pack_dataset
from mapvoice_llm.pack_schema import GENERIC_ENTITY_FIELDS
from mapvoice_llm.regional_packs import RegionalPack


def test_verified_policy_excludes_unverified(tmp_path):
    (tmp_path / "configs").mkdir()
    (tmp_path / "configs/language_profiles.json").write_text(
        json.dumps({
            "profiles": [{
                "language_code": "ta",
                "language": "Tamil",
                "script_name": "Tamil",
                "unicode_ranges": [["0B80", "0BFF"]],
                "tts_language_code": "ta-IN"
            }]
        })
    )

    path = tmp_path / "entities.csv"
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=GENERIC_ENTITY_FIELDS)
        writer.writeheader()
        writer.writerow({
            "entity_id": "a",
            "latin_name": "One",
            "native_name": "தமிழ்",
            "entity_type": "locality",
            "city": "City",
            "language": "Tamil",
            "language_code": "ta",
            "alternate_spellings": "",
            "morphemes": "",
            "suffix": "",
            "verification_status": "unverified",
            "pronunciation_verified": "false",
            "source_name": "",
            "source_url": "",
            "source_type": "",
            "reviewer": "",
            "notes": "",
        })
        writer.writerow({
            "entity_id": "b",
            "latin_name": "Two",
            "native_name": "தமிழ்",
            "entity_type": "locality",
            "city": "City",
            "language": "Tamil",
            "language_code": "ta",
            "alternate_spellings": "",
            "morphemes": "",
            "suffix": "",
            "verification_status": "verified",
            "pronunciation_verified": "false",
            "source_name": "source",
            "source_url": "",
            "source_type": "",
            "reviewer": "",
            "notes": "",
        })

    pack = RegionalPack(
        pack_id="x-ta",
        city="City",
        state="State",
        country="India",
        region_language="Tamil",
        region_language_code="ta",
        navigation_languages=["English", "Tamil"],
        entity_file="entities.csv",
        candidate_file=None,
        evaluation_suites=[],
    )

    result = build_pack_dataset(
        project_root=tmp_path,
        pack=pack,
        entity_repository=RegionalEntityRepository(path),
        policy_id="verified",
    )

    assert result.source_entities == 2
    assert result.included_entities == 1
    assert result.total_examples == 8
