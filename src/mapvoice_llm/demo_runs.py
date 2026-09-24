from __future__ import annotations

import json
import time
import uuid
from pathlib import Path


class DemoRunStore:
    """
    Lightweight local JSON run archive for development/demo use.

    This is intentionally not a production database. Each run is a standalone
    JSON document that can be inspected, compared, or exported.
    """

    def __init__(self, root: str | Path):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def create(self, payload: dict) -> dict:
        run_id = f"run_{uuid.uuid4().hex[:12]}"
        stored = {
            "run_id": run_id,
            "created_at_epoch": time.time(),
            **payload,
        }
        (self.root / f"{run_id}.json").write_text(
            json.dumps(stored, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return stored

    def get(self, run_id: str) -> dict | None:
        path = self.root / f"{run_id}.json"
        if not path.exists():
            return None
        return json.loads(path.read_text(encoding="utf-8"))

    def list(self, limit: int = 20) -> list[dict]:
        items = []
        paths = sorted(
            self.root.glob("run_*.json"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )
        for path in paths[:limit]:
            try:
                items.append(json.loads(path.read_text(encoding="utf-8")))
            except Exception:
                continue
        return items
