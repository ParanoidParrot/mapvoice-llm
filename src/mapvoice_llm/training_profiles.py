from __future__ import annotations
import json
from dataclasses import dataclass, asdict
from pathlib import Path

@dataclass(frozen=True)
class TrainingProfile:
    profile_id: str
    label: str
    description: str
    quantization: str
    epochs: int
    learning_rate: float
    batch_size: int
    gradient_accumulation_steps: int
    recommended_device: str
    notes: str = ""
    def to_dict(self) -> dict:
        return asdict(self)

class TrainingProfileRegistry:
    def __init__(self, path: str | Path):
        self.path = Path(path)
    def _load(self) -> dict:
        return json.loads(self.path.read_text(encoding="utf-8"))
    def list(self) -> list[TrainingProfile]:
        return [TrainingProfile(**row) for row in self._load().get("profiles", [])]
    def get(self, profile_id: str) -> TrainingProfile:
        for profile in self.list():
            if profile.profile_id == profile_id:
                return profile
        raise KeyError(profile_id)
    def default(self) -> TrainingProfile:
        data = self._load()
        if data.get("default_profile_id"):
            return self.get(data["default_profile_id"])
        profiles = self.list()
        if not profiles:
            raise RuntimeError("No training profiles configured")
        return profiles[0]
