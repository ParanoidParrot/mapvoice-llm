from __future__ import annotations

from dataclasses import dataclass
import re


KANNADA_RANGE_RE = re.compile(r"[\u0C80-\u0CFF]")


def contains_kannada(text: str | None) -> bool:
    """Legacy compatibility helper retained for Bengaluru tests/tools."""
    return bool(text and KANNADA_RANGE_RE.search(text))


@dataclass(frozen=True)
class PronunciationTarget:
    native_script: str | None
    spoken_form: str | None
    phonetic_form: str | None = None
    representation: str = "native-script"


def build_target(
    *,
    native_name: str | None = None,
    fallback_name: str | None,
    # Legacy Bengaluru call sites may still pass this.
    kannada_name: str | None = None,
) -> PronunciationTarget:
    native_script = (
        (native_name or kannada_name or "").strip()
        or None
    )

    if native_script:
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
