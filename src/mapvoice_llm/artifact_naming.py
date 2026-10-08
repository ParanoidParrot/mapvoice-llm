from __future__ import annotations

import re


def normalize_component(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r'[^a-z0-9]+', '-', value)
    return value.strip('-')


def default_adapter_id(*, pack_id: str, version: str) -> str:
    return f"mapvoice-{normalize_component(pack_id)}-{normalize_component(version)}"
