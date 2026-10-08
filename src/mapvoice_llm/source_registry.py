from __future__ import annotations
import json
from dataclasses import dataclass, asdict
from pathlib import Path

@dataclass(frozen=True)
class SourceDefinition:
    source_id: str
    label: str
    source_type: str
    homepage: str | None
    license: str
    attribution: str | None
    allowed_pack_ids: list[str]
    acquisition_mode: str
    notes: str = ""

    def to_dict(self) -> dict:
        return asdict(self)

class SourceRegistry:
    def __init__(self, path: str | Path):
        self.path = Path(path)

    def list(self) -> list[SourceDefinition]:
        data = json.loads(self.path.read_text(encoding="utf-8"))
        return [SourceDefinition(**row) for row in data.get("sources", [])]

    def get(self, source_id: str) -> SourceDefinition:
        for item in self.list():
            if item.source_id == source_id:
                return item
        raise KeyError(source_id)
