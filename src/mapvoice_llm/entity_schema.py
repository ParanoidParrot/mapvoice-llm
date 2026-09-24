from __future__ import annotations
from dataclasses import dataclass


@dataclass
class EntityRecord:
    entity_id: str
    english_name: str
    kannada_name: str
    entity_type: str
    city: str
    language: str
    alternate_spellings: str = ""
    morphemes: str = ""
    suffix: str = ""
    verification_status: str = "unverified"
    pronunciation_verified: str = "false"
    source_name: str = ""
    source_url: str = ""
    source_type: str = ""
    reviewer: str = ""
    notes: str = ""

    @property
    def verified(self) -> bool:
        return self.verification_status.strip().lower() == "verified"

    @property
    def pronunciation_is_verified(self) -> bool:
        return self.pronunciation_verified.strip().lower() == "true"
