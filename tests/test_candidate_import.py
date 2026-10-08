import csv

from mapvoice_llm.candidate_import import import_candidates
from mapvoice_llm.pack_context import PackContext
from mapvoice_llm.pack_schema import GENERIC_CANDIDATE_FIELDS, GENERIC_ENTITY_FIELDS
from mapvoice_llm.regional_packs import RegionalPack


def test_candidate_import_deduplicates(tmp_path):
    entity_path = tmp_path / "entities.csv"
    with entity_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=GENERIC_ENTITY_FIELDS)
        writer.writeheader()
        writer.writerow({
            "entity_id": "e1",
            "latin_name": "Existing",
            "native_name": "Native",
            "entity_type": "locality",
            "city": "City",
            "language": "Tamil",
            "language_code": "ta",
            "alternate_spellings": "",
            "morphemes": "",
            "suffix": "",
            "verification_status": "reviewed",
            "pronunciation_verified": "false",
            "source_name": "source",
            "source_url": "",
            "source_type": "",
            "reviewer": "",
            "notes": "",
        })

    candidate_path = tmp_path / "candidates.csv"
    with candidate_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=GENERIC_CANDIDATE_FIELDS)
        writer.writeheader()

    source = tmp_path / "source.csv"
    with source.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["latin_name", "source_name"],
        )
        writer.writeheader()
        writer.writerow({"latin_name": "Existing", "source_name": "src"})
        writer.writerow({"latin_name": "New Place", "source_name": "src"})
        writer.writerow({"latin_name": "New Place", "source_name": "src"})

    pack = RegionalPack(
        pack_id="x-ta",
        city="City",
        state="State",
        country="India",
        region_language="Tamil",
        region_language_code="ta",
        navigation_languages=["English", "Tamil"],
        entity_file="entities.csv",
        candidate_file="candidates.csv",
        evaluation_suites=[],
    )

    context = PackContext(
        project_root=tmp_path,
        pack=pack,
    )

    result = import_candidates(
        context=context,
        source_csv=source,
    )

    assert result.imported == 1
    assert result.skipped_existing_entity == 1
    assert result.skipped_existing_candidate == 1
