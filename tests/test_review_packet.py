import csv

from mapvoice_llm.review_packet import build_review_packet
from mapvoice_llm.pack_schema import GENERIC_CANDIDATE_FIELDS


def test_review_packet_builds(tmp_path):
    candidate = tmp_path / "candidates.csv"

    with candidate.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=GENERIC_CANDIDATE_FIELDS)
        writer.writeheader()
        row = {field: "" for field in GENERIC_CANDIDATE_FIELDS}
        row.update({
            "candidate_id": "c1",
            "latin_name": "Adyar",
            "entity_type": "locality",
            "annotation_status": "candidate",
        })
        writer.writerow(row)

    output = tmp_path / "packet.csv"

    result = build_review_packet(
        project_root=tmp_path,
        pack_id="chn-ta",
        candidate_csv=candidate,
        output=output,
    )

    assert result["rows"] == 1
    assert output.exists()
