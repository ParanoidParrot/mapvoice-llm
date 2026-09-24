from __future__ import annotations
from dataclasses import dataclass

KNOWN_SUFFIXES = (
    "agrahara", "nagara", "layout", "halli", "pura", "puram",
    "nagar", "palya", "kere", "kunte", "sandra", "bhavi",
    "gudi", "kote", "pete", "pet", "cross", "road",
)

@dataclass(frozen=True)
class MorphologyGuess:
    name: str
    suffix: str | None
    stem: str
    confidence: str

def guess_suffix(name: str) -> MorphologyGuess:
    compact = "".join(ch for ch in name.strip() if ch.isalnum()).lower()
    for suffix in sorted(KNOWN_SUFFIXES, key=len, reverse=True):
        if compact.endswith(suffix) and len(compact) > len(suffix):
            return MorphologyGuess(
                name=name,
                suffix=suffix,
                stem=compact[:-len(suffix)],
                confidence="heuristic",
            )
    return MorphologyGuess(name=name, suffix=None, stem=compact, confidence="none")
