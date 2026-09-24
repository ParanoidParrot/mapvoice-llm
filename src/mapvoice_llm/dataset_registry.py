from __future__ import annotations
import json
from pathlib import Path

class DatasetRegistry:
    def __init__(self, registry_path: str | Path):
        self.path = Path(registry_path)
        self.data = json.loads(self.path.read_text(encoding="utf-8"))

    @property
    def current(self) -> dict:
        return self.data["versions"][self.data["current_version"]]

    def resolve(self, key: str, project_root: str | Path) -> Path:
        return Path(project_root) / self.current[key]
