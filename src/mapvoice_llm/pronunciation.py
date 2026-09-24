from __future__ import annotations

import re
from dataclasses import dataclass


KANNADA_RANGE_RE = re.compile(r"[\u0C80-\u0CFF]")


@dataclass(frozen=True)
class PronunciationTarget:
    """
    v0.3 separates three concepts that were previously conflated:

    - native_script: Kannada-script canonical form where known
    - spoken_form: text intended for downstream TTS
    - phonetic_form: optional future phoneme/IPA-like representation

    We intentionally do NOT invent phonemes in v0.3. That field remains nullable until
    we select and validate a representation suitable for Kannada pronunciation.
    """

    native_script: str | None
    spoken_form: str | None
    phonetic_form: str | None = None
    representation: str = "native-script"


def contains_kannada(text: str | None) -> bool:
    return bool(text and KANNADA_RANGE_RE.search(text))


def build_target(
    *,
    kannada_name: str | None,
    fallback_name: str | None,
) -> PronunciationTarget:
    native_script = (kannada_name or "").strip() or None

    if native_script and contains_kannada(native_script):
        return PronunciationTarget(
            native_script=native_script,
            spoken_form=native_script,
            phonetic_form=None,
            representation="native-script",
        )

    fallback = (fallback_name or "").strip() or None
    return PronunciationTarget(
        native_script=None,
        spoken_form=fallback,
        phonetic_form=None,
        representation="english-script-fallback",
    )
