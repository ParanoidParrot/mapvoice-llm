from __future__ import annotations

import json
from collections import Counter
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROCESSED = PROJECT_ROOT / "data" / "processed"


def read_jsonl(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def main() -> None:
    files = {
        name: PROCESSED / f"{name}.jsonl"
        for name in ("train", "validation", "test")
    }

    splits = {name: read_jsonl(path) for name, path in files.items()}
    errors: list[str] = []
    warnings: list[str] = []

    entity_sets = {
        name: {row["entity_id"] for row in rows}
        for name, rows in splits.items()
    }

    pairs = [
        ("train", "validation"),
        ("train", "test"),
        ("validation", "test"),
    ]
    for left, right in pairs:
        overlap = entity_sets[left] & entity_sets[right]
        if overlap:
            errors.append(f"{left}/{right} entity leakage: {sorted(overlap)}")

    for split_name, rows in splits.items():
        example_ids = [row["example_id"] for row in rows]
        duplicates = [
            value
            for value, count in Counter(example_ids).items()
            if count > 1
        ]
        if duplicates:
            errors.append(
                f"{split_name}: duplicate example ids: {duplicates[:10]}"
            )

        for row in rows:
            target = row.get("target") or {}
            if not target.get("place_name"):
                errors.append(
                    f"{split_name}/{row.get('example_id')}: missing place_name"
                )
            if not target.get("spoken_form"):
                warnings.append(
                    f"{split_name}/{row.get('example_id')}: missing spoken_form"
                )

    print(f"Errors: {len(errors)}")
    print(f"Warnings: {len(warnings)}")
    for item in errors:
        print(f"ERROR: {item}")
    for item in warnings[:25]:
        print(f"WARN : {item}")

    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
