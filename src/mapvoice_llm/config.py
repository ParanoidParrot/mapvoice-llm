from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _load_dotenv() -> None:
    """
    Load project-root .env when python-dotenv is available.

    The import is optional so the core API can still start without the optional
    TTS dependency group installed.
    """
    try:
        from dotenv import load_dotenv
    except ImportError:
        return

    load_dotenv(PROJECT_ROOT / ".env", override=False)


_load_dotenv()


def _env_bool(name: str, default: bool = False) -> bool:
    raw = os.getenv(name)
    if raw is None or not raw.strip():
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _tts_enabled() -> bool:
    # Explicit MAPVOICE_TTS_ENABLED wins. If omitted/blank, a configured API key
    # automatically enables TTS, which is friendlier for local development.
    raw = os.getenv("MAPVOICE_TTS_ENABLED")
    if raw is not None and raw.strip():
        return raw.strip().lower() in {"1", "true", "yes", "on"}
    return bool((os.getenv("SARVAM_API_KEY") or "").strip())


@dataclass(frozen=True)
class Settings:
    pack_id: str | None = os.getenv("MAPVOICE_PACK_ID") or None

    model_name: str | None = os.getenv(
        "MAPVOICE_MODEL_NAME",
        "sarvamai/sarvam-1",
    ) or None
    adapter_path: str | None = os.getenv("MAPVOICE_ADAPTER_PATH") or None
    device: str = os.getenv("MAPVOICE_DEVICE", "auto")

    tts_enabled: bool = _tts_enabled()
    tts_provider: str = os.getenv("MAPVOICE_TTS_PROVIDER", "sarvam")
    sarvam_api_key: str | None = os.getenv("SARVAM_API_KEY") or None

    # Current Sarvam defaults. Override from .env if desired.
    sarvam_tts_model: str = os.getenv("SARVAM_TTS_MODEL", "bulbul:v3")
    sarvam_tts_speaker: str = os.getenv("SARVAM_TTS_SPEAKER", "shubh")

    # Compatibility fallback. The active regional pack normally supplies the
    # native-language code.
    sarvam_tts_target_language: str = os.getenv(
        "SARVAM_TTS_TARGET_LANGUAGE",
        "kn-IN",
    )

    tts_english_language: str = os.getenv(
        "MAPVOICE_TTS_ENGLISH_LANGUAGE",
        "en-IN",
    )


settings = Settings()
