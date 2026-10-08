from __future__ import annotations

from pathlib import Path

from .entity_repository import RegionalEntityRepository


class RegionalLexicon:
    def __init__(self, csv_path: str | Path):
        self.repository = RegionalEntityRepository(csv_path)
        self.entities = self.repository.list()

        self._names = []
        for entity in self.entities:
            names = [entity.latin_name]
            names.extend(
                item.strip()
                for item in (
                    entity.alternate_spellings or ""
                ).split("|")
                if item.strip()
            )

            for name in names:
                if name:
                    self._names.append(
                        (name.casefold(), entity)
                    )

        self._names.sort(
            key=lambda item: len(item[0]),
            reverse=True,
        )

    def find_in_text(self, text: str):
        lowered = text.casefold()
        for name, entity in self._names:
            if name in lowered:
                return entity
        return None

    def get_by_id(self, entity_id: str):
        for entity in self.entities:
            if entity.entity_id == entity_id:
                return entity
        return None


# Backward compatibility.
BengaluruLexicon = RegionalLexicon
