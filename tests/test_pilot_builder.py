import csv

from mapvoice_llm.pack_schema import GENERIC_ENTITY_FIELDS
from mapvoice_llm.pilot_builder import build_pilot
from mapvoice_llm.pilot_profiles import PilotProfile
from mapvoice_llm.regional_packs import RegionalPack


def test_pilot_builds_from_verified_reviewed_entities(tmp_path):
    reviewed = tmp_path / "data/reviewed/chn-ta/entities.csv"
    reviewed.parent.mkdir(parents=True)

    with reviewed.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=GENERIC_ENTITY_FIELDS)
        writer.writeheader()

        for i in range(12):
            writer.writerow({
                "entity_id": f"e{i}",
                "latin_name": f"Place {i}",
                "native_name": f"தமிழ்{i}",
                "entity_type": "locality",
                "city": "Chennai",
                "language": "Tamil",
                "language_code": "ta",
                "alternate_spellings": "",
                "morphemes": "",
                "suffix": "",
                "verification_status": "verified",
                "pronunciation_verified": "false",
                "source_name": "source",
                "source_url": "",
                "source_type": "test",
                "reviewer": "a|b",
                "notes": "",
            })

    pack = RegionalPack(
        pack_id="chn-ta",
        city="Chennai",
        state="Tamil Nadu",
        country="India",
        region_language="Tamil",
        region_language_code="ta",
        navigation_languages=["English", "Tamil"],
        entity_file="entities.csv",
        candidate_file=None,
        evaluation_suites=[],
    )

    profile = PilotProfile(
        pack_id="chn-ta",
        minimum_verified_entities=12,
        train_entities=8,
        validation_entities=2,
        test_entities=2,
    )

    result = build_pilot(
        project_root=tmp_path,
        pack=pack,
        profile=profile,
    )

    assert result["built"]
    assert result["manifest"]["entity_split"] == {
        "train": 8,
        "validation": 2,
        "test": 2,
    }
