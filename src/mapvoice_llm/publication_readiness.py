from __future__ import annotations
import csv
from pathlib import Path


def assess_release(release_dir: str | Path) -> dict:
    release_dir = Path(release_dir)

    def read(name: str) -> list[dict]:
        path = release_dir / "data" / name
        if not path.exists():
            return []
        with path.open(newline="", encoding="utf-8") as handle:
            return list(csv.DictReader(handle))

    preview = read("preview.csv")
    reviewed = read("reviewed.csv")
    reviewed_packs = {row["pack_id"] for row in reviewed}
    pronunciation_rows = [
        row for row in reviewed
        if row.get("pronunciation_verified") == "true"
    ]

    return {
        "preview_rows": len(preview),
        "reviewed_rows": len(reviewed),
        "reviewed_pack_count": len(reviewed_packs),
        "pronunciation_verified_rows": len(pronunciation_rows),
        "allowed_public_claims": {
            "early_preview_dataset": len(preview) > 0,
            "reviewed_dataset": len(reviewed) > 0,
            "reviewed_multilingual_dataset": len(reviewed_packs) >= 2,
            "pronunciation_verified_dataset": len(pronunciation_rows) >= 20,
            "training_ready_multilingual_dataset": False,
        },
    }
