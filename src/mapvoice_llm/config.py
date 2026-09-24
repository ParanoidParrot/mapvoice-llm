from dataclasses import dataclass
import os


def _env_bool(name: str, default: bool = False) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    model_name: str | None = os.getenv(
        "MAPVOICE_MODEL_NAME",
        "sarvamai/sarvam-1",
    ) or None
    adapter_path: str | None = os.getenv("MAPVOICE_ADAPTER_PATH") or None
    device: str = os.getenv("MAPVOICE_DEVICE", "auto")

    tts_enabled: bool = _env_bool("MAPVOICE_TTS_ENABLED", False)
    tts_provider: str = os.getenv("MAPVOICE_TTS_PROVIDER", "sarvam")
    sarvam_api_key: str | None = os.getenv("SARVAM_API_KEY") or None

    # These are deliberately configurable because provider SDK/model names can evolve.
    sarvam_tts_model: str = os.getenv("SARVAM_TTS_MODEL", "bulbul:v2")
    sarvam_tts_speaker: str = os.getenv("SARVAM_TTS_SPEAKER", "anushka")
    sarvam_tts_target_language: str = os.getenv(
        "SARVAM_TTS_TARGET_LANGUAGE",
        "kn-IN",
    )


settings = Settings()
