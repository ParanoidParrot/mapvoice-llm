from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from threading import Lock


ALLOWED_STATUS = {"candidate", "reviewed", "rejected"}


@dataclass
class CandidateUpdate:
    annotation_status: str | None = None
    native_name: str | None = None
    source_name: str | None = None
    source_url: str | None = None
    notes: str | None = None

    # Backward-compatible alias for the existing Bengaluru candidate file.
    kannada_name: str | None = None


class CandidateRepository:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self._lock = Lock()

    def _read(self) -> tuple[list[str], list[dict]]:
        with self.path.open(newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            return list(reader.fieldnames or []), list(reader)

    @staticmethod
    def _normalized(row: dict) -> dict:
        result = dict(row)
        result["latin_name"] = (
            row.get("latin_name")
            or row.get("english_name")
            or ""
        )
        result["native_name"] = (
            row.get("native_name")
            or row.get("kannada_name")
            or ""
        )
        return result

    def list(
        self,
        *,
        status: str | None = None,
        limit: int = 100,
    ) -> list[dict]:
        _, rows = self._read()

        if status:
            rows = [
                row
                for row in rows
                if row.get("annotation_status") == status
            ]

        return [self._normalized(row) for row in rows[:limit]]

    def get(self, candidate_id: str) -> dict | None:
        _, rows = self._read()
        for row in rows:
            if row["candidate_id"] == candidate_id:
                return self._normalized(row)
        return None

    def update(self, candidate_id: str, update: CandidateUpdate) -> dict | None:
        with self._lock:
            fieldnames, rows = self._read()
            found = None

            native_field = (
                "native_name"
                if "native_name" in fieldnames
                else "kannada_name"
            )

            for row in rows:
                if row["candidate_id"] != candidate_id:
                    continue

                values = {
                    "annotation_status": update.annotation_status,
                    native_field: (
                        update.native_name
                        if update.native_name is not None
                        else update.kannada_name
                    ),
                    "source_name": update.source_name,
                    "source_url": update.source_url,
                    "notes": update.notes,
                }

                for key, value in values.items():
                    if value is not None and key in fieldnames:
                        row[key] = value

                if row["annotation_status"] not in ALLOWED_STATUS:
                    raise ValueError(
                        f"Invalid annotation_status: "
                        f"{row['annotation_status']}"
                    )

                found = self._normalized(row)
                break

            if found is None:
                return None

            tmp = self.path.with_suffix(".tmp")
            with tmp.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)
            tmp.replace(self.path)

            return found

    def stats(self) -> dict:
        _, rows = self._read()

        def native_value(row: dict) -> str:
            return row.get("native_name") or row.get("kannada_name") or ""

        return {
            "total": len(rows),
            "candidate": sum(
                row["annotation_status"] == "candidate" for row in rows
            ),
            "reviewed": sum(
                row["annotation_status"] == "reviewed" for row in rows
            ),
            "rejected": sum(
                row["annotation_status"] == "rejected" for row in rows
            ),
            "with_native_name": sum(
                bool(native_value(row).strip()) for row in rows
            ),
            # Legacy response field retained for older UI consumers.
            "with_kannada_name": sum(
                bool(native_value(row).strip()) for row in rows
            ),
            "with_source": sum(
                bool(row["source_name"].strip()) for row in rows
            ),
        }
