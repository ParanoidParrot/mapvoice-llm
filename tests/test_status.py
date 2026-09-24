from pathlib import Path
import csv

from mapvoice_llm.status import dataset_status


def test_dataset_status(tmp_path: Path):
    source = tmp_path / "entities.csv"
    fields = [
        "entity_id",
        "entity_type",
        "verification_status",
        "pronunciation_verified",
    ]

    with source.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerow({
            "entity_id": "x",
            "entity_type": "locality",
            "verification_status": "verified",
            "pronunciation_verified": "true",
        })

    result = dataset_status(source)
    assert result["entities"] == 1
    assert result["verified"] == 1
    assert result["pronunciation_verified"] == 1
