from __future__ import annotations

from .base import TTSResult


class DisabledTTSProvider:
    name = "disabled"

    def __init__(self, reason: str = "TTS is not configured"):
        self.reason = reason

    @property
    def available(self) -> bool:
        return False

    def synthesize(self, text: str, *, language_code: str | None = None) -> TTSResult:
        raise RuntimeError(self.reason)
