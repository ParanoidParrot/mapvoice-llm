from __future__ import annotations

import json
import time
import uuid
from pathlib import Path


class TrainingRunStore:
    def __init__(self, root: str | Path):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def start(self, payload: dict) -> dict:
        run_id = f"train_{uuid.uuid4().hex[:12]}"
        record = {
            "run_id": run_id,
            "status": "running",
            "started_at_epoch": time.time(),
            **payload,
        }
        self._write(record)
        return record

    def finish(
        self,
        run_id: str,
        *,
        output_dir: str,
        metrics: dict | None = None,
    ) -> dict:
        record = self.get(run_id)
        if record is None:
            raise KeyError(run_id)

        record.update({
            "status": "completed",
            "finished_at_epoch": time.time(),
            "output_dir": output_dir,
            "metrics": metrics or {},
        })
        self._write(record)
        return record

    def fail(self, run_id: str, error: str) -> dict:
        record = self.get(run_id)
        if record is None:
            raise KeyError(run_id)

        record.update({
            "status": "failed",
            "finished_at_epoch": time.time(),
            "error": error,
        })
        self._write(record)
        return record

    def get(self, run_id: str) -> dict | None:
        path = self.root / f"{run_id}.json"
        if not path.exists():
            return None
        return json.loads(path.read_text(encoding="utf-8"))

    def list(self, limit: int = 50) -> list[dict]:
        paths = sorted(
            self.root.glob("train_*.json"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )
        rows = []

        for path in paths[:limit]:
            try:
                rows.append(json.loads(path.read_text(encoding="utf-8")))
            except Exception:
                continue

        return rows

    def _write(self, record: dict) -> None:
        path = self.root / f"{record['run_id']}.json"
        path.write_text(
            json.dumps(record, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
