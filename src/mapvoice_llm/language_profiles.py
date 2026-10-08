from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass(frozen=True)
class LanguageProfile:
    language_code: str
    language: str
    script_name: str
    unicode_ranges: list[list[str]]
    tts_language_code: str

    def to_dict(self) -> dict:
        return asdict(self)

    def codepoint_in_script(self, codepoint: int) -> bool:
        for start_hex, end_hex in self.unicode_ranges:
            if int(start_hex, 16) <= codepoint <= int(end_hex, 16):
                return True
        return False


class LanguageProfileRegistry:
    def __init__(self, path: str | Path):
        self.path = Path(path)

    def list(self) -> list[LanguageProfile]:
        data = json.loads(self.path.read_text(encoding="utf-8"))
        return [LanguageProfile(**row) for row in data.get("profiles", [])]

    def get(self, language_code: str) -> LanguageProfile:
        for profile in self.list():
            if profile.language_code == language_code:
                return profile
        raise KeyError(language_code)
