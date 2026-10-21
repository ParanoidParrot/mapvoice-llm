from __future__ import annotations

import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


def _row_hash(row: dict) -> str:
    canonical = json.dumps(
        row,
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":"),
    )
    return hashlib.sha256(
        canonical.encode("utf-8")
    ).hexdigest()


def snapshot_csv(
    path: str | Path,
    *,
    key_field: str,
) -> dict:
    path = Path(path)

    if not path.exists():
        return {
            "path": str(path),
            "rows": 0,
            "records": {},
        }

    with path.open(
        newline="",
        encoding="utf-8",
    ) as handle:
        rows = list(csv.DictReader(handle))

    records = {}
    for row in rows:
        key = row.get(key_field, "")
        if key:
            records[key] = {
                "hash": _row_hash(row),
                "row": row,
            }

    return {
        "path": str(path),
        "rows": len(rows),
        "records": records,
    }


def compare_snapshots(
    first: dict,
    second: dict,
) -> dict:
    first_records = first.get("records", {})
    second_records = second.get("records", {})

    first_keys = set(first_records)
    second_keys = set(second_records)

    added = sorted(
        second_keys - first_keys
    )
    removed = sorted(
        first_keys - second_keys
    )
    shared = first_keys & second_keys

    changed = sorted(
        key
        for key in shared
        if (
            first_records[key]["hash"]
            != second_records[key]["hash"]
        )
    )

    return {
        "first_rows": first.get("rows", 0),
        "second_rows": second.get("rows", 0),
        "added": len(added),
        "removed": len(removed),
        "changed": len(changed),
        "unchanged": (
            len(shared) - len(changed)
        ),
        "added_keys": added,
        "removed_keys": removed,
        "changed_keys": changed,
    }


def write_release_snapshot(
    *,
    release_dir: str | Path,
) -> dict:
    release_dir = Path(release_dir)

    preview = snapshot_csv(
        release_dir
        / "data"
        / "preview.csv",
        key_field="record_id",
    )
    reviewed = snapshot_csv(
        release_dir
        / "data"
        / "reviewed.csv",
        key_field="record_id",
    )

    payload = {
        "created_at": datetime.now(
            timezone.utc
        ).isoformat(),
        "preview": {
            "rows": preview["rows"],
            "records": {
                key: value["hash"]
                for key, value
                in preview["records"].items()
            },
        },
        "reviewed": {
            "rows": reviewed["rows"],
            "records": {
                key: value["hash"]
                for key, value
                in reviewed["records"].items()
            },
        },
    }

    path = (
        release_dir
        / "dataset_snapshot.json"
    )
    path.write_text(
        json.dumps(
            payload,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    return payload
