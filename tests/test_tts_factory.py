from mapvoice_llm.config import Settings
from mapvoice_llm.tts.factory import build_tts_provider


def test_tts_disabled_by_default():
    provider = build_tts_provider(
        Settings(
            tts_enabled=False,
            tts_provider="sarvam",
            sarvam_api_key=None,
        )
    )
    assert provider.available is False


def test_tts_missing_key_is_unavailable():
    provider = build_tts_provider(
        Settings(
            tts_enabled=True,
            tts_provider="sarvam",
            sarvam_api_key=None,
        )
    )
    assert provider.available is False
