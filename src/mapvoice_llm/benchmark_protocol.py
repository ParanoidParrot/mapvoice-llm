from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class BenchmarkProtocol:
    protocol_id: str
    protocol_version: int
    seed: int
    primary_metrics: list[str]
    secondary_metrics: list[str]
    required_slices: list[str]
    minimum_test_examples: dict[str, int]
    paired_bootstrap: dict
    ranking: list[dict]
    notes: str = ""

    @classmethod
    def load(cls, path: str | Path) -> "BenchmarkProtocol":
        return cls(**json.loads(Path(path).read_text(encoding="utf-8")))

    def to_dict(self) -> dict:
        return {
            "protocol_id": self.protocol_id,
            "protocol_version": self.protocol_version,
            "seed": self.seed,
            "primary_metrics": self.primary_metrics,
            "secondary_metrics": self.secondary_metrics,
            "required_slices": self.required_slices,
            "minimum_test_examples": self.minimum_test_examples,
            "paired_bootstrap": self.paired_bootstrap,
            "ranking": self.ranking,
            "notes": self.notes,
        }
