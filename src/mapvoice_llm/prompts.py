from __future__ import annotations

import json

SYSTEM_PROMPT = """You are MapVoice-BLR-KN, a narrowly scoped Bengaluru navigation-language model.

Given a navigation instruction:
1. identify the relevant Bengaluru place entity,
2. preserve its common English-script name,
3. produce a Kannada-aware spoken form,
4. return valid JSON only.

Do not invent a place name that is not present in the instruction.
Do not fabricate a phonetic representation. If no validated phonetic form exists, return null.
"""

OUTPUT_SCHEMA = {
    "place_name": "string|null",
    "place_name_kn": "string|null",
    "entity_type": "string|null",
    "language_origin": "string|null",
    "spoken_form": "string|null",
    "phonetic_form": "string|null",
    "pronunciation_representation": "string|null",
}


def build_prompt(
    *,
    text: str,
    city: str = "Bengaluru",
    region_language: str = "Kannada",
    navigation_language: str = "English",
) -> str:
    payload = {
        "city": city,
        "region_language": region_language,
        "navigation_language": navigation_language,
        "text": text,
    }

    return (
        f"{SYSTEM_PROMPT}\n\n"
        "INPUT:\n"
        f"{json.dumps(payload, ensure_ascii=False)}\n\n"
        "OUTPUT SCHEMA:\n"
        f"{json.dumps(OUTPUT_SCHEMA, ensure_ascii=False)}\n\n"
        "OUTPUT:\n"
    )


def canonical_target(target: dict) -> dict:
    return {
        "place_name": target.get("place_name"),
        "place_name_kn": target.get("place_name_kn"),
        "entity_type": target.get("entity_type"),
        "language_origin": target.get("language_origin"),
        "spoken_form": target.get("spoken_form")
        or target.get("pronunciation_form"),
        "phonetic_form": target.get("phonetic_form"),
        "pronunciation_representation": target.get(
            "pronunciation_representation", "native-script"
        ),
    }


def format_sft_example(record: dict) -> dict:
    prompt = build_prompt(**record["input"])
    completion = json.dumps(canonical_target(record["target"]), ensure_ascii=False)
    return {
        "prompt": prompt,
        "completion": completion,
        "text": prompt + completion,
    }
