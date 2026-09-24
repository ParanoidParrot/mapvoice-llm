from __future__ import annotations

import json
import re
from dataclasses import dataclass


@dataclass
class ParsedModelOutput:
    data: dict | None
    raw_text: str
    valid_json: bool
    error: str | None = None


def _extract_first_json_object(text: str) -> str | None:
    """
    Extract the first balanced JSON object from generated text.

    This is intentionally small and dependency-free. It handles quoted braces and escapes.
    """
    start = text.find("{")
    if start < 0:
        return None

    depth = 0
    in_string = False
    escaped = False

    for i in range(start, len(text)):
        ch = text[i]

        if escaped:
            escaped = False
            continue

        if ch == "\\" and in_string:
            escaped = True
            continue

        if ch == '"':
            in_string = not in_string
            continue

        if in_string:
            continue

        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return text[start : i + 1]

    return None


def parse_model_output(text: str) -> ParsedModelOutput:
    candidate = _extract_first_json_object(text)
    if candidate is None:
        return ParsedModelOutput(
            data=None,
            raw_text=text,
            valid_json=False,
            error="No JSON object found",
        )

    try:
        parsed = json.loads(candidate)
    except json.JSONDecodeError as exc:
        return ParsedModelOutput(
            data=None,
            raw_text=text,
            valid_json=False,
            error=str(exc),
        )

    if not isinstance(parsed, dict):
        return ParsedModelOutput(
            data=None,
            raw_text=text,
            valid_json=False,
            error="Model output JSON is not an object",
        )

    return ParsedModelOutput(
        data=parsed,
        raw_text=text,
        valid_json=True,
    )
