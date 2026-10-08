from __future__ import annotations

import hashlib
import re
from pathlib import Path


def _slug(text: str, limit: int = 56) -> str:
    value = re.sub(
        r"[^a-zA-Z0-9]+",
        "_",
        text.strip().lower(),
    ).strip("_")
    return (value or "audio")[:limit]


class AudioStore:
    def __init__(self, root: str | Path):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def path_for(
        self,
        *,
        kind: str,
        text: str,
        extension: str = "wav",
        cache_key: str = "",
    ) -> Path:
        digest = hashlib.sha256(
            (
                kind
                + "\0"
                + text
                + "\0"
                + cache_key
            ).encode("utf-8")
        ).hexdigest()[:12]

        filename = (
            f"{kind}_{_slug(text)}_{digest}.{extension}"
        )
        return self.root / filename

    def existing(
        self,
        *,
        kind: str,
        text: str,
        extension: str = "wav",
        cache_key: str = "",
    ) -> Path | None:
        path = self.path_for(
            kind=kind,
            text=text,
            extension=extension,
            cache_key=cache_key,
        )
        return path if path.exists() else None

    def save(
        self,
        *,
        kind: str,
        text: str,
        audio_bytes: bytes,
        extension: str = "wav",
        cache_key: str = "",
    ) -> Path:
        path = self.path_for(
            kind=kind,
            text=text,
            extension=extension,
            cache_key=cache_key,
        )

        if not path.exists():
            path.write_bytes(audio_bytes)

        return path

    def url_for(self, path: Path) -> str:
        return f"/audio/{path.name}"
