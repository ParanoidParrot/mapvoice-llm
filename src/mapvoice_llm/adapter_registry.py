from __future__ import annotations

import json
import time
from pathlib import Path
from threading import Lock


class AdapterRegistry:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = Lock()

        if not self.path.exists():
            self._write({"active_adapter_id": None, "adapters": []})

    def _read(self) -> dict:
        return json.loads(self.path.read_text(encoding="utf-8"))

    def _write(self, data: dict) -> None:
        self.path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def list(self) -> list[dict]:
        return self._read().get("adapters", [])

    def get(self, adapter_id: str) -> dict | None:
        for adapter in self.list():
            if adapter["adapter_id"] == adapter_id:
                return adapter
        return None

    def active(self) -> dict | None:
        data = self._read()
        adapter_id = data.get("active_adapter_id")
        return self.get(adapter_id) if adapter_id else None

    def register(self, record: dict) -> dict:
        with self._lock:
            data = self._read()
            adapters = data.setdefault("adapters", [])

            adapter_id = record["adapter_id"]
            existing_index = next(
                (
                    index
                    for index, item in enumerate(adapters)
                    if item["adapter_id"] == adapter_id
                ),
                None,
            )

            stored = {
                "registered_at_epoch": time.time(),
                "status": "candidate",
                **record,
            }

            if existing_index is None:
                adapters.append(stored)
            else:
                adapters[existing_index] = {
                    **adapters[existing_index],
                    **stored,
                }

            self._write(data)
            return stored

    def promote(self, adapter_id: str) -> dict:
        with self._lock:
            data = self._read()
            found = None

            for adapter in data.get("adapters", []):
                if adapter["adapter_id"] == adapter_id:
                    adapter["status"] = "active"
                    adapter["promoted_at_epoch"] = time.time()
                    found = dict(adapter)
                elif adapter.get("status") == "active":
                    adapter["status"] = "candidate"

            if found is None:
                raise KeyError(adapter_id)

            data["active_adapter_id"] = adapter_id
            self._write(data)
            return found

    def clear_active(self) -> None:
        with self._lock:
            data = self._read()
            active_id = data.get("active_adapter_id")

            for adapter in data.get("adapters", []):
                if adapter["adapter_id"] == active_id:
                    adapter["status"] = "candidate"

            data["active_adapter_id"] = None
            self._write(data)
