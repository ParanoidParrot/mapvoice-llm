from __future__ import annotations

import argparse
import csv
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from mapvoice_llm.pack_context import load_pack_context
from mapvoice_llm.pack_schema import GENERIC_ENTITY_FIELDS


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pack-id", default="blr-kn")
    parser.add_argument("--output")
    args = parser.parse_args()

    context = load_pack_context(PROJECT_ROOT, args.pack_id)
    entities = context.entity_repository.list()

    output = (
        Path(args.output)
        if args.output
        else PROJECT_ROOT
        / "outputs"
        / "generic_entities"
        / f"{args.pack_id}_entities.csv"
    )
    output.parent.mkdir(parents=True, exist_ok=True)

    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=GENERIC_ENTITY_FIELDS,
        )
        writer.writeheader()

        for entity in entities:
            writer.writerow({
                "entity_id": entity.entity_id,
                "latin_name": entity.latin_name,
                "native_name": entity.native_name,
                "entity_type": entity.entity_type,
                "city": entity.city,
                "language": entity.language,
                "language_code": entity.language_code or "",
                "alternate_spellings": entity.alternate_spellings,
                "morphemes": entity.morphemes,
                "suffix": entity.suffix,
                "verification_status": entity.verification_status,
                "pronunciation_verified": (
                    "true" if entity.pronunciation_verified else "false"
                ),
                "source_name": entity.source_name,
                "source_url": entity.source_url,
                "source_type": entity.source_type,
                "reviewer": entity.reviewer,
                "notes": entity.notes,
            })

    print(output)


if __name__ == "__main__":
    main()
