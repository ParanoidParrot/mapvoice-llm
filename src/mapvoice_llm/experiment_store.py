from __future__ import annotations

import json
import time
import uuid
from pathlib import Path


class ExperimentStore:
    def __init__(self, root: str | Path):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def save(self, payload: dict) -> dict:
        experiment_id = f"exp_{uuid.uuid4().hex[:12]}"
        stored = {
            "experiment_id": experiment_id,
            "created_at_epoch": time.time(),
            **payload,
        }
        path = self.root / f"{experiment_id}.json"
        path.write_text(
            json.dumps(stored, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return stored

    def get(self, experiment_id: str) -> dict | None:
        path = self.root / f"{experiment_id}.json"
        if not path.exists():
            return None
        return json.loads(path.read_text(encoding="utf-8"))

    def list(self, limit: int = 20) -> list[dict]:
        items = []
        paths = sorted(
            self.root.glob("exp_*.json"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )
        for path in paths[:limit]:
            try:
                items.append(json.loads(path.read_text(encoding="utf-8")))
            except Exception:
                continue
        return items
