from __future__ import annotations

import json
from pathlib import Path

from .dataset_snapshot import (
    compare_snapshots,
    snapshot_csv,
)


def compare_release_dirs(
    first_dir: str | Path,
    second_dir: str | Path,
) -> dict:
    first_dir = Path(first_dir)
    second_dir = Path(second_dir)

    preview = compare_snapshots(
        snapshot_csv(
            first_dir / "data/preview.csv",
            key_field="record_id",
        ),
        snapshot_csv(
            second_dir / "data/preview.csv",
            key_field="record_id",
        ),
    )

    reviewed = compare_snapshots(
        snapshot_csv(
            first_dir / "data/reviewed.csv",
            key_field="record_id",
        ),
        snapshot_csv(
            second_dir / "data/reviewed.csv",
            key_field="record_id",
        ),
    )

    return {
        "first_release": str(first_dir),
        "second_release": str(second_dir),
        "preview": preview,
        "reviewed": reviewed,
    }


def write_release_diff(
    *,
    first_dir: str | Path,
    second_dir: str | Path,
    output: str | Path,
) -> dict:
    diff = compare_release_dirs(
        first_dir,
        second_dir,
    )

    output = Path(output)
    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )
    output.write_text(
        json.dumps(
            diff,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    return diff
