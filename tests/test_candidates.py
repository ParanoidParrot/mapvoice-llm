import csv

from mapvoice_llm.candidates import CandidateRepository, CandidateUpdate


def seed(path):
    fields = [
        "candidate_id",
        "english_name",
        "entity_type",
        "city",
        "region_language",
        "annotation_status",
        "kannada_name",
        "source_name",
        "source_url",
        "notes",
    ]

    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerow({
            "candidate_id": "cand_1",
            "english_name": "Example",
            "entity_type": "locality",
            "city": "Bengaluru",
            "region_language": "Kannada",
            "annotation_status": "candidate",
            "kannada_name": "",
            "source_name": "",
            "source_url": "",
            "notes": "",
        })


def test_candidate_update(tmp_path):
    path = tmp_path / "candidates.csv"
    seed(path)

    repo = CandidateRepository(path)
    updated = repo.update(
        "cand_1",
        CandidateUpdate(
            kannada_name="ಉದಾಹರಣೆ",
            source_name="manual",
            annotation_status="reviewed",
        ),
    )

    assert updated is not None
    assert updated["annotation_status"] == "reviewed"
    assert repo.stats()["reviewed"] == 1
