from __future__ import annotations

from ..config import Settings
from .disabled import DisabledTTSProvider
from .sarvam import SarvamTTSProvider


def build_tts_provider(
    settings: Settings,
    *,
    default_language_code: str | None = None,
):
    if not settings.tts_enabled:
        return DisabledTTSProvider(
            "TTS is disabled. Set SARVAM_API_KEY or "
            "MAPVOICE_TTS_ENABLED=true."
        )

    if settings.tts_provider == "sarvam":
        if not settings.sarvam_api_key:
            return DisabledTTSProvider(
                "TTS is enabled but SARVAM_API_KEY is missing."
            )

        return SarvamTTSProvider(
            api_key=settings.sarvam_api_key,
            model=settings.sarvam_tts_model,
            speaker=settings.sarvam_tts_speaker,
            target_language_code=(
                default_language_code
                or settings.sarvam_tts_target_language
            ),
        )

    return DisabledTTSProvider(
        f"Unsupported TTS provider: {settings.tts_provider}"
    )
