import base64
import sys
import types

from mapvoice_llm.tts.sarvam import SarvamTTSProvider


class FakeResponse:
    def __init__(self):
        self.audios = [
            base64.b64encode(b"RIFFfake").decode()
        ]


class FakeTextToSpeech:
    def __init__(self):
        self.calls = []

    def convert(self, **kwargs):
        self.calls.append(kwargs)
        return FakeResponse()


class FakeClient:
    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.text_to_speech = FakeTextToSpeech()


def test_current_sarvam_sdk_shape(monkeypatch):
    module = types.ModuleType("sarvamai")
    module.SarvamAI = FakeClient
    monkeypatch.setitem(
        sys.modules,
        "sarvamai",
        module,
    )

    provider = SarvamTTSProvider(
        api_key="test-key",
        model="bulbul:v3",
        speaker="shubh",
        target_language_code="kn-IN",
    )

    result = provider.synthesize(
        "hello",
        language_code="en-IN",
    )

    assert result.audio_bytes == b"RIFFfake"
    assert (
        provider._client.kwargs[
            "api_subscription_key"
        ]
        == "test-key"
    )

    call = provider._client.text_to_speech.calls[0]
    assert call["language_code"] == "en-IN"
    assert call["model"] == "bulbul:v3"
