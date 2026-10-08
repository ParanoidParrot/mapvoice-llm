from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass(frozen=True)
class RegionalPack:
    pack_id: str
    city: str
    state: str
    country: str
    region_language: str
    region_language_code: str
    navigation_languages: list[str]
    entity_file: str
    candidate_file: str | None
    evaluation_suites: list[str]
    default_base_model: str | None = None
    default_tts_language_code: str | None = None
    status: str = 'experimental'
    description: str | None = None

    def to_dict(self) -> dict:
        return asdict(self)


class RegionalPackRegistry:
    def __init__(self, path: str | Path):
        self.path = Path(path)

    def _load(self) -> dict:
        if not self.path.exists():
            return {'default_pack_id': None, 'packs': []}
        return json.loads(self.path.read_text(encoding='utf-8'))

    def list(self) -> list[RegionalPack]:
        data = self._load()
        return [RegionalPack(**row) for row in data.get('packs', [])]

    def get(self, pack_id: str) -> RegionalPack:
        for pack in self.list():
            if pack.pack_id == pack_id:
                return pack
        raise KeyError(pack_id)

    def default(self) -> RegionalPack:
        data = self._load()
        pack_id = data.get('default_pack_id')
        if pack_id:
            return self.get(pack_id)
        packs = self.list()
        if not packs:
            raise RuntimeError('No regional packs configured')
        return packs[0]
