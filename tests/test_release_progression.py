import csv
import json

from mapvoice_llm.release_progression import assess_release_progression


def test_preview_release_stays_preview_without_reviewed_rows(tmp_path):
    (tmp_path / "configs").mkdir()
    (tmp_path / "configs/release_policy.json").write_text(
        json.dumps({
            "preview": {
                "minimum_preview_rows": 1
            },
            "reviewed": {
                "minimum_reviewed_rows": 20,
                "minimum_reviewed_packs": 1
            },
            "multilingual-reviewed": {
                "minimum_reviewed_rows": 40,
                "minimum_reviewed_packs": 2
            },
            "pilot": {
                "minimum_ready_pilots": 1
            },
        })
    )

    release = tmp_path / "release/data"
    release.mkdir(parents=True)

    fields = ["record_id", "pack_id"]

    with (
        release / "preview.csv"
    ).open(
        "w",
        newline="",
        encoding="utf-8",
    ) as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=fields,
        )
        writer.writeheader()
        writer.writerow({
            "record_id": "1",
            "pack_id": "chn-ta",
        })

    with (
        release / "reviewed.csv"
    ).open(
        "w",
        newline="",
        encoding="utf-8",
    ) as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=fields,
        )
        writer.writeheader()

    result = assess_release_progression(
        project_root=tmp_path,
        release_dir=tmp_path / "release",
    )

    assert result["gates"]["preview"]
    assert not result["gates"]["reviewed"]
    assert result["suggested_next_release"] == "0.1.x-preview"
