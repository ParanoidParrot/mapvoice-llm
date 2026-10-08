from __future__ import annotations

import base64
import importlib.util
import os
import sys

from .base import TTSResult


class SarvamTTSProvider:
    """
    Sarvam text-to-speech adapter.

    Current Sarvam REST/SDK behavior:
      - client: SarvamAI(api_subscription_key=...)
      - request parameter: language_code
      - response.audios: list of base64-encoded audio strings

    The decoder also accepts older object/.content response shapes so existing
    local installations fail more gracefully.
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
        if not self.api_key:
            return False
        try:
            return importlib.util.find_spec("sarvamai") is not None
        except (ImportError, ValueError):
            return "sarvamai" in sys.modules

    @property
    def reason(self) -> str | None:
        if not self.api_key:
            return "SARVAM_API_KEY is not configured"
        if not self.available:
            return (
                "The sarvamai SDK is not installed. Run: "
                "python -m pip install -r requirements-tts.txt"
            )
        return None

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
                "Run: python -m pip install -r requirements-tts.txt"
            ) from exc

        try:
            # Current SDK.
            self._client = SarvamAI(
                api_subscription_key=self.api_key,
            )
        except TypeError:
            # Backward-compatible fallback for older SDK installs.
            os.environ.setdefault("SARVAM_API_KEY", self.api_key)
            self._client = SarvamAI()

        return self._client

    @staticmethod
    def _decode_audio_item(item) -> bytes:
        if isinstance(item, (bytes, bytearray)):
            return bytes(item)

        if isinstance(item, str):
            try:
                return base64.b64decode(item)
            except Exception as exc:
                raise RuntimeError(
                    "Unable to base64-decode Sarvam audio"
                ) from exc

        # Older SDK shape used by the original MapVoice POC.
        content = getattr(item, "content", None)
        if content is not None:
            if isinstance(content, str):
                try:
                    return base64.b64decode(content)
                except Exception as exc:
                    raise RuntimeError(
                        "Unable to base64-decode Sarvam audio .content"
                    ) from exc
            if isinstance(content, (bytes, bytearray)):
                return bytes(content)

        raise RuntimeError(
            "Unsupported Sarvam audio response item: "
            f"{type(item).__name__}"
        )

    def synthesize(
        self,
        text: str,
        *,
        language_code: str | None = None,
    ) -> TTSResult:
        text = text.strip()
        if not text:
            raise ValueError("TTS text cannot be empty")

        client = self._get_client()
        selected_language = (
            language_code
            or self.target_language_code
        )

        try:
            response = client.text_to_speech.convert(
                text=text,
                language_code=selected_language,
                speaker=self.speaker,
                model=self.model,
            )
        except TypeError as exc:
            # Very old SDK compatibility: it used target_language_code.
            try:
                response = client.text_to_speech.convert(
                    text=text,
                    target_language_code=selected_language,
                    speaker=self.speaker,
                    model=self.model,
                )
            except Exception:
                raise RuntimeError(
                    "Sarvam TTS request failed. The installed SDK may not "
                    "match the configured provider adapter."
                ) from exc
        except Exception as exc:
            raise RuntimeError(
                f"Sarvam TTS request failed: {exc}"
            ) from exc

        audios = getattr(response, "audios", None)
        if not audios:
            raise RuntimeError("Sarvam response contained no audio")

        chunks = [
            self._decode_audio_item(item)
            for item in audios
        ]
        audio_bytes = b"".join(chunks)

        if not audio_bytes:
            raise RuntimeError("Sarvam returned empty audio bytes")

        return TTSResult(
            audio_bytes=audio_bytes,
            extension="wav",
            content_type="audio/wav",
            provider=self.name,
        )
