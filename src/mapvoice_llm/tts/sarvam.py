from __future__ import annotations

import os

from .base import TTSResult


class SarvamTTSProvider:
    """
    Thin optional Sarvam SDK adapter.

    The SDK is imported lazily, so API/rule/model development does not require
    the sarvamai package. This follows the working MapVoice integration pattern:
    SarvamAI() reads SARVAM_API_KEY from the environment and audio bytes are
    taken from response.audios[0].content.

    Model/speaker/language are environment-configurable rather than hardcoded
    into the rest of MapVoice-LLM.
    """

    name = "sarvam"

    def __init__(
        self,
        *,
        api_key: str | None,
        model: str,
        speaker: str,
        target_language_code: str,
    ):
        self.api_key = api_key
        self.model = model
        self.speaker = speaker
        self.target_language_code = target_language_code
        self._client = None

    @property
    def available(self) -> bool:
        return bool(self.api_key)

    def _get_client(self):
        if not self.api_key:
            raise RuntimeError("SARVAM_API_KEY is not configured")

        if self._client is not None:
            return self._client

        try:
            from sarvamai import SarvamAI
        except ImportError as exc:
            raise RuntimeError(
                "Sarvam TTS requested but 'sarvamai' is not installed. "
                "Install requirements-tts.txt."
            ) from exc

        # Existing MapVoice integration used SarvamAI() with the environment var.
        os.environ.setdefault("SARVAM_API_KEY", self.api_key)
        self._client = SarvamAI()
        return self._client

    def synthesize(
        self,
        text: str,
        *,
        language_code: str | None = None,
    ) -> TTSResult:
        if not text.strip():
            raise ValueError("TTS text cannot be empty")

        client = self._get_client()
        target_language = language_code or self.target_language_code

        try:
            response = client.text_to_speech.convert(
                text=text,
                target_language_code=target_language,
                speaker=self.speaker,
                model=self.model,
            )
        except AttributeError as exc:
            raise RuntimeError(
                "Installed sarvamai SDK does not expose "
                "client.text_to_speech.convert with the expected interface. "
                "Check the installed SDK version and provider adapter."
            ) from exc

        audios = getattr(response, "audios", None)
        if not audios:
            raise RuntimeError("Sarvam response contained no audio")

        content = getattr(audios[0], "content", None)
        if content is None:
            raise RuntimeError("Sarvam audio result contained no .content")

        if isinstance(content, str):
            # Some SDK versions/providers may expose base64 strings instead.
            import base64
            try:
                content = base64.b64decode(content)
            except Exception as exc:
                raise RuntimeError("Unable to decode Sarvam audio content") from exc

        if not isinstance(content, (bytes, bytearray)):
            raise RuntimeError(
                f"Unexpected Sarvam audio content type: {type(content).__name__}"
            )

        return TTSResult(
            audio_bytes=bytes(content),
            extension="wav",
            content_type="audio/wav",
            provider=self.name,
        )
