from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from mapvoice_llm.config import settings
from mapvoice_llm.pack_context import load_pack_context
from mapvoice_llm.tts import build_tts_provider


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pack-id")
    parser.add_argument(
        "--synthesize",
        action="store_true",
        help="Make one real Sarvam TTS request.",
    )
    parser.add_argument(
        "--text",
        default="MapVoice text to speech test.",
    )
    args = parser.parse_args()

    context = load_pack_context(
        PROJECT_ROOT,
        args.pack_id or settings.pack_id,
    )

    native_language = (
        context.pack.default_tts_language_code
        or settings.sarvam_tts_target_language
    )

    provider = build_tts_provider(
        settings,
        default_language_code=native_language,
    )

    report = {
        "pack_id": context.pack.pack_id,
        "tts_enabled": settings.tts_enabled,
        "provider": settings.tts_provider,
        "api_key_configured": bool(
            settings.sarvam_api_key
        ),
        "sarvamai_installed": (
            importlib.util.find_spec("sarvamai")
            is not None
        ),
        "available": bool(
            getattr(provider, "available", False)
        ),
        "reason": getattr(
            provider,
            "reason",
            None,
        ),
        "model": settings.sarvam_tts_model,
        "speaker": settings.sarvam_tts_speaker,
        "english_language": (
            settings.tts_english_language
        ),
        "native_language": native_language,
    }

    print(json.dumps(
        report,
        ensure_ascii=False,
        indent=2,
    ))

    if not args.synthesize:
        return

    if not provider.available:
        raise SystemExit(
            "TTS provider is not available."
        )

    result = provider.synthesize(
        args.text,
        language_code=settings.tts_english_language,
    )

    output = (
        PROJECT_ROOT
        / "outputs"
        / "generated_audio"
        / "tts_diagnostic.wav"
    )
    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )
    output.write_bytes(result.audio_bytes)

    print(f"Wrote: {output}")


if __name__ == "__main__":
    main()
