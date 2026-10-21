import csv

from mapvoice_llm.release_diff import compare_release_dirs


FIELDS = ["record_id", "latin_name"]


def write_release(root, name, rows):
    path = root / name / "data"
    path.mkdir(parents=True)

    with (
        path / "preview.csv"
    ).open(
        "w",
        newline="",
        encoding="utf-8",
    ) as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=FIELDS,
        )
        writer.writeheader()
        writer.writerows(rows)

    with (
        path / "reviewed.csv"
    ).open(
        "w",
        newline="",
        encoding="utf-8",
    ) as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=FIELDS,
        )
        writer.writeheader()

    return root / name


def test_release_diff_tracks_added_and_changed(tmp_path):
    first = write_release(
        tmp_path,
        "a",
        [
            {
                "record_id": "1",
                "latin_name": "One",
            }
        ],
    )

    second = write_release(
        tmp_path,
        "b",
        [
            {
                "record_id": "1",
                "latin_name": "Changed",
            },
            {
                "record_id": "2",
                "latin_name": "Two",
            },
        ],
    )

    result = compare_release_dirs(
        first,
        second,
    )

    assert result["preview"]["added"] == 1
    assert result["preview"]["changed"] == 1
