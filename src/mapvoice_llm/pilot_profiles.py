from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass(frozen=True)
class PilotProfile:
    pack_id: str
    minimum_verified_entities: int
    train_entities: int
    validation_entities: int
    test_entities: int

    def to_dict(self) -> dict:
        return asdict(self)


class PilotProfileRegistry:
    def __init__(
        self,
        path: str | Path,
    ):
        self.path = Path(
            path
        )

    def list(
        self,
    ) -> list[
        PilotProfile
    ]:
        data = json.loads(
            self.path.read_text(
                encoding="utf-8"
            )
        )
        return [
            PilotProfile(
                **row
            )
            for row in data.get(
                "profiles",
                [],
            )
        ]

    def get(
        self,
        pack_id: str,
    ) -> PilotProfile:
        for item in self.list():
            if (
                item.pack_id
                == pack_id
            ):
                return item

        raise KeyError(
            pack_id
        )
