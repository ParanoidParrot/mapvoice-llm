from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass
class TTSResult:
    audio_bytes: bytes
    extension: str = "wav"
    content_type: str = "audio/wav"
    provider: str = "unknown"


class TTSProvider(Protocol):
    name: str

    @property
    def available(self) -> bool:
        ...

    def synthesize(
        self,
        text: str,
        *,
        language_code: str | None = None,
    ) -> TTSResult:
        ...
