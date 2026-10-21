import csv

from mapvoice_llm.candidate_conflicts import audit_candidate_conflicts


def test_candidate_conflict_detects_native_disagreement(tmp_path):
    path = tmp_path / "candidates.csv"

    with path.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "candidate_id",
                "latin_name",
                "native_name",
                "source_id",
                "source_record_id",
            ],
        )
        writer.writeheader()
        writer.writerow({
            "candidate_id": "1",
            "latin_name": "Place",
            "native_name": "A",
            "source_id": "s1",
            "source_record_id": "1",
        })
        writer.writerow({
            "candidate_id": "2",
            "latin_name": "Place",
            "native_name": "B",
            "source_id": "s2",
            "source_record_id": "2",
        })

    result = audit_candidate_conflicts(path)

    assert result["duplicate_name_groups"] == 1
    assert result["native_name_conflicts"] == 1
    assert result["multi_source_name_groups"] == 1
