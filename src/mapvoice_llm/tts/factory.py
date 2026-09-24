from __future__ import annotations

from ..config import Settings
from .disabled import DisabledTTSProvider
from .sarvam import SarvamTTSProvider


def build_tts_provider(settings: Settings):
    if not settings.tts_enabled:
        return DisabledTTSProvider("MAPVOICE_TTS_ENABLED is false")

    if settings.tts_provider == "sarvam":
        if not settings.sarvam_api_key:
            return DisabledTTSProvider(
                "MAPVOICE_TTS_ENABLED is true but SARVAM_API_KEY is missing"
            )
        return SarvamTTSProvider(
            api_key=settings.sarvam_api_key,
            model=settings.sarvam_tts_model,
            speaker=settings.sarvam_tts_speaker,
            target_language_code=settings.sarvam_tts_target_language,
        )

    return DisabledTTSProvider(
        f"Unsupported TTS provider: {settings.tts_provider}"
    )
