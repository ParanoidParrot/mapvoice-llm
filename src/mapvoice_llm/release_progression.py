from __future__ import annotations

import csv
import json
from pathlib import Path


def _read_csv(path: Path) -> list[dict]:
    if not path.exists():
        return []

    with path.open(
        newline="",
        encoding="utf-8",
    ) as handle:
        return list(
            csv.DictReader(handle)
        )


def assess_release_progression(
    *,
    project_root: str | Path,
    release_dir: str | Path,
) -> dict:
    project_root = Path(project_root)
    release_dir = Path(release_dir)

    policy = json.loads(
        (
            project_root
            / "configs"
            / "release_policy.json"
        ).read_text(encoding="utf-8")
    )

    preview = _read_csv(
        release_dir
        / "data"
        / "preview.csv"
    )
    reviewed = _read_csv(
        release_dir
        / "data"
        / "reviewed.csv"
    )

    reviewed_packs = {
        row["pack_id"]
        for row in reviewed
    }

    pilot_manifests = list(
        (
            project_root
            / "data"
            / "pilots"
        ).glob("*/manifest.json")
    )
    ready_pilots = len(
        pilot_manifests
    )

    gates = {
        "preview": (
            len(preview)
            >= policy["preview"][
                "minimum_preview_rows"
            ]
        ),
        "reviewed": (
            len(reviewed)
            >= policy["reviewed"][
                "minimum_reviewed_rows"
            ]
            and len(reviewed_packs)
            >= policy["reviewed"][
                "minimum_reviewed_packs"
            ]
        ),
        "multilingual-reviewed": (
            len(reviewed)
            >= policy[
                "multilingual-reviewed"
            ][
                "minimum_reviewed_rows"
            ]
            and len(reviewed_packs)
            >= policy[
                "multilingual-reviewed"
            ][
                "minimum_reviewed_packs"
            ]
        ),
        "pilot": (
            ready_pilots
            >= policy["pilot"][
                "minimum_ready_pilots"
            ]
        ),
    }

    if gates["pilot"]:
        suggested = "0.3.0-pilot"
    elif gates[
        "multilingual-reviewed"
    ]:
        suggested = (
            "0.2.0-multilingual-reviewed"
        )
    elif gates["reviewed"]:
        suggested = "0.2.0-reviewed"
    else:
        suggested = "0.1.x-preview"

    return {
        "preview_rows": len(preview),
        "reviewed_rows": len(reviewed),
        "reviewed_pack_count": (
            len(reviewed_packs)
        ),
        "ready_pilot_count": (
            ready_pilots
        ),
        "gates": gates,
        "suggested_next_release": (
            suggested
        ),
    }
