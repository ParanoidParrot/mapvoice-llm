import csv

from mapvoice_llm.review_packet_import import import_review_packet
from mapvoice_llm.review_store import ReviewStore


def test_review_packet_import_appends_events(tmp_path):
    packet = tmp_path / "packet.csv"

    with packet.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "candidate_id",
                "decision",
                "reviewer_native_name",
                "source_approved",
                "pronunciation_approved",
                "review_notes",
            ],
        )
        writer.writeheader()
        writer.writerow({
            "candidate_id": "c1",
            "decision": "approve",
            "reviewer_native_name": "தமிழ்",
            "source_approved": "true",
            "pronunciation_approved": "false",
            "review_notes": "ok",
        })

    result = import_review_packet(
        project_root=tmp_path,
        pack_id="chn-ta",
        reviewer_id="reviewer-a",
        packet_csv=packet,
    )

    assert result.events_appended == 1

    events = ReviewStore(
        tmp_path,
        "chn-ta",
    ).list()

    assert events[0]["candidate_id"] == "c1"
    assert events[0]["source_approved"]
