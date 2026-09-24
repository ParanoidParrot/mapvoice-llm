from __future__ import annotations

import csv
from pathlib import Path


class BengaluruLexicon:
    def __init__(self, csv_path: str | Path):
        self.rows: list[dict] = []
        with open(csv_path, newline="", encoding="utf-8") as handle:
            self.rows = list(csv.DictReader(handle))

        self._names: list[tuple[str, dict]] = []
        for row in self.rows:
            names = [row["english_name"]]
            aliases = [
                item.strip()
                for item in (row.get("alternate_spellings") or "").split("|")
                if item.strip()
            ]
            names.extend(aliases)

            for name in names:
                self._names.append((name.lower(), row))

        self._names.sort(key=lambda item: len(item[0]), reverse=True)

    def find_in_text(self, text: str) -> dict | None:
        lowered = text.lower()
        for name, row in self._names:
            if name in lowered:
                return row
        return None

    def get_by_id(self, entity_id: str) -> dict | None:
        for row in self.rows:
            if row["entity_id"] == entity_id:
                return row
        return None
