from __future__ import annotations

from collections import defaultdict


MORPHOLOGY_SUFFIXES = (
    "nagar",
    "halli",
    "pura",
    "kere",
    "palya",
    "gudi",
    "kote",
    "bhavi",
    "kunte",
    "sandra",
)


def classify_example(row: dict) -> set[str]:
    slices = {"all"}
    target = row.get("target") or {}
    metadata = row.get("metadata") or {}
    native = target.get("place_name_native") or target.get("place_name_kn") or ""

    if native:
        slices.add("native-script")

    suffix = (metadata.get("suffix") or "").strip().casefold()
    latin = (target.get("place_name") or "").casefold()

    if suffix or any(token in latin for token in MORPHOLOGY_SUFFIXES):
        slices.add("morphology")

    if metadata.get("split_role") == "entity-held-out":
        slices.add("entity-held-out")

    return slices


def slice_examples(rows: list[dict]) -> dict[str, list[dict]]:
    result: dict[str, list[dict]] = defaultdict(list)

    for row in rows:
        for slice_id in classify_example(row):
            result[slice_id].append(row)

    return dict(result)
