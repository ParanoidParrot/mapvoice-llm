from __future__ import annotations

import json
from pathlib import Path

from .review_models import ReviewEvent


class ReviewStore:
    def __init__(
        self,
        project_root: str | Path,
        pack_id: str,
    ):
        self.path = (
            Path(project_root)
            / "data"
            / "reviews"
            / pack_id
            / "events.jsonl"
        )
        self.path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

    def append(
        self,
        event: ReviewEvent,
    ) -> None:
        with self.path.open(
            "a",
            encoding="utf-8",
        ) as handle:
            handle.write(
                json.dumps(
                    event.to_dict(),
                    ensure_ascii=False,
                )
                + "\n"
            )

    def list(self) -> list[dict]:
        if not self.path.exists():
            return []

        with self.path.open(
            encoding="utf-8",
        ) as handle:
            return [
                json.loads(line)
                for line in handle
                if line.strip()
            ]

    def for_candidate(
        self,
        candidate_id: str,
    ) -> list[dict]:
        return [
            row
            for row in self.list()
            if row["candidate_id"]
            == candidate_id
        ]
