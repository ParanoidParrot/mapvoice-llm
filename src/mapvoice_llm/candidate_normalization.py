from __future__ import annotations
import re
import unicodedata

def normalize_name(value: str) -> str:
    value = unicodedata.normalize("NFKC", value or "")
    value = value.strip().casefold()
    value = re.sub(r"[^\w\s-]+", " ", value, flags=re.UNICODE)
    value = re.sub(r"[\s_-]+", " ", value).strip()
    return value

def coordinate_key(lat: str | None, lon: str | None) -> str | None:
    try:
        if lat is None or lon is None or lat == "" or lon == "":
            return None
        return f"{round(float(lat), 5)},{round(float(lon), 5)}"
    except (TypeError, ValueError):
        return None
