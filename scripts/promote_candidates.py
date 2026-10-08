from __future__ import annotations

import argparse
import csv
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from mapvoice_llm.candidates import CandidateRepository
from mapvoice_llm.pack_context import load_pack_context


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pack-id")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    context = load_pack_context(
        PROJECT_ROOT,
        args.pack_id,
    )

    if context.candidate_csv is None:
        raise SystemExit("Pack has no candidate file")

    candidates = CandidateRepository(
        context.candidate_csv
    ).list(limit=100000)

    with context.entity_csv.open(
        newline="",
        encoding="utf-8",
    ) as handle:
        reader = csv.DictReader(handle)
        entities = list(reader)
        fieldnames = list(reader.fieldnames or [])

    generic = (
        "latin_name" in fieldnames
        and "native_name" in fieldnames
    )

    def entity_name(row):
        return (
            row.get("latin_name")
            or row.get("english_name")
            or ""
        )

    existing_names = {
        entity_name(row).strip().casefold()
        for row in entities
    }

    promotable = []
    for row in candidates:
        if row.get(
            "annotation_status",
            "",
        ).strip().lower() != "reviewed":
            continue

        native_name = (
            row.get("native_name")
            or row.get("kannada_name")
            or ""
        ).strip()

        latin_name = (
            row.get("latin_name")
            or row.get("english_name")
            or ""
        ).strip()

        if not native_name:
            continue
        if not row.get(
            "source_name",
            "",
        ).strip():
            continue
        if latin_name.casefold() in existing_names:
            continue

        promotable.append(row)

    print(
        f"Pack: {context.pack.pack_id}"
    )
    print(
        f"Promotable candidates: {len(promotable)}"
    )
    for row in promotable:
        print(
            "- "
            + (
                row.get("latin_name")
                or row.get("english_name")
                or ""
            )
            + " -> "
            + (
                row.get("native_name")
                or row.get("kannada_name")
                or ""
            )
        )

    if args.dry_run or not promotable:
        return

    existing_ids = {
        row["entity_id"]
        for row in entities
    }
    prefix = context.pack.pack_id.replace(
        "-",
        "_",
    )
    next_index = 1

    def next_id():
        nonlocal next_index
        while (
            f"{prefix}_{next_index:04d}"
            in existing_ids
        ):
            next_index += 1
        value = (
            f"{prefix}_{next_index:04d}"
        )
        existing_ids.add(value)
        next_index += 1
        return value

    with context.entity_csv.open(
        "a",
        newline="",
        encoding="utf-8",
    ) as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=fieldnames,
        )

        for row in promotable:
            latin_name = (
                row.get("latin_name")
                or row.get("english_name")
                or ""
            )
            native_name = (
                row.get("native_name")
                or row.get("kannada_name")
                or ""
            )

            if generic:
                output = {
                    "entity_id": next_id(),
                    "latin_name": latin_name,
                    "native_name": native_name,
                    "entity_type": row.get(
                        "entity_type",
                        "locality",
                    ),
                    "city": context.pack.city,
                    "language": (
                        context.pack.region_language
                    ),
                    "language_code": (
                        context.pack.region_language_code
                    ),
                    "alternate_spellings": "",
                    "morphemes": "",
                    "suffix": "",
                    "verification_status": "reviewed",
                    "pronunciation_verified": "false",
                    "source_name": row.get(
                        "source_name",
                        "",
                    ),
                    "source_url": row.get(
                        "source_url",
                        "",
                    ),
                    "source_type": "candidate-promotion",
                    "reviewer": "",
                    "notes": row.get("notes", ""),
                }
            else:
                output = {
                    "entity_id": next_id(),
                    "english_name": latin_name,
                    "kannada_name": native_name,
                    "entity_type": row.get(
                        "entity_type",
                        "locality",
                    ),
                    "city": context.pack.city,
                    "language": (
                        context.pack.region_language
                    ),
                    "alternate_spellings": "",
                    "morphemes": "",
                    "suffix": "",
                    "verification_status": "reviewed",
                    "pronunciation_verified": "false",
                    "source_name": row.get(
                        "source_name",
                        "",
                    ),
                    "source_url": row.get(
                        "source_url",
                        "",
                    ),
                    "source_type": "candidate-promotion",
                    "reviewer": "",
                    "notes": row.get("notes", ""),
                }

            writer.writerow(output)

    print(
        f"Appended {len(promotable)} rows "
        f"to {context.entity_csv}"
    )


if __name__ == "__main__":
    main()
