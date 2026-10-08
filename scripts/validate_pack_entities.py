from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from mapvoice_llm.pack_context import load_pack_context


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pack-id")
    args = parser.parse_args()

    context = load_pack_context(
        PROJECT_ROOT,
        args.pack_id,
    )
    rows = context.entity_repository.list()

    errors = []
    warnings = []

    ids = [
        item.entity_id.strip()
        for item in rows
    ]
    duplicate_ids = [
        value
        for value, count in Counter(ids).items()
        if count > 1
    ]
    if duplicate_ids:
        errors.append(
            f"Duplicate entity IDs: {duplicate_ids}"
        )

    names = [
        item.latin_name.strip().casefold()
        for item in rows
        if item.latin_name.strip()
    ]
    duplicate_names = [
        value
        for value, count in Counter(names).items()
        if count > 1
    ]
    if duplicate_names:
        warnings.append(
            f"Duplicate names: {duplicate_names}"
        )

    for item in rows:
        if (
            item.verification_status
            == "verified"
            and not item.source_name.strip()
        ):
            warnings.append(
                f"{item.entity_id}: verified without source"
            )
        if (
            item.pronunciation_verified
            and not item.reviewer.strip()
        ):
            warnings.append(
                f"{item.entity_id}: pronunciation verified without reviewer"
            )

    print(
        f"Pack: {context.pack.pack_id}"
    )
    print(f"Rows: {len(rows)}")
    print(f"Errors: {len(errors)}")
    print(f"Warnings: {len(warnings)}")

    for error in errors:
        print("ERROR:", error)
    for warning in warnings:
        print("WARN :", warning)

    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
