from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass(frozen=True)
class BaseModelDefinition:
    model_key: str
    hf_model_id: str
    label: str
    parameter_scale: str
    license_family: str
    commercial_use: str
    access: str
    indic_specialization: bool
    benchmark_enabled: bool
    notes: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


class BaseModelRegistry:
    def __init__(self, path: str | Path):
        self.path = Path(path)

    def _load(self) -> dict:
        return json.loads(self.path.read_text(encoding="utf-8"))

    def list(self) -> list[BaseModelDefinition]:
        return [
            BaseModelDefinition(**row)
            for row in self._load().get("models", [])
        ]

    def get(self, model_key: str) -> BaseModelDefinition:
        for model in self.list():
            if model.model_key == model_key:
                return model
        raise KeyError(model_key)

    def reference(self) -> BaseModelDefinition:
        key = self._load()["reference_model_key"]
        return self.get(key)

    def benchmark_models(self) -> list[BaseModelDefinition]:
        return [model for model in self.list() if model.benchmark_enabled]
