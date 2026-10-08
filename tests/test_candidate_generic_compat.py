import csv

from mapvoice_llm.candidates import CandidateRepository, CandidateUpdate
from mapvoice_llm.pack_schema import GENERIC_CANDIDATE_FIELDS


def test_generic_candidate_update(tmp_path):
    path = tmp_path / "candidates.csv"
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=GENERIC_CANDIDATE_FIELDS)
        writer.writeheader()
        writer.writerow({
            "candidate_id": "c1",
            "latin_name": "Example",
            "entity_type": "locality",
            "city": "City",
            "region_language": "Language",
            "region_language_code": "xx",
            "annotation_status": "candidate",
            "native_name": "",
            "source_name": "",
            "source_url": "",
            "notes": "",
        })

    repo = CandidateRepository(path)
    updated = repo.update(
        "c1",
        CandidateUpdate(
            native_name="Native",
            annotation_status="reviewed",
        ),
    )

    assert updated["native_name"] == "Native"
    assert repo.stats()["reviewed"] == 1
