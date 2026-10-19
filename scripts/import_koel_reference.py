from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from mapvoice_llm.language_profiles import LanguageProfileRegistry
from mapvoice_llm.language_validation import native_script_fraction
from mapvoice_llm.pack_context import load_pack_context


LANGUAGE_NAMES = {
    "kn": "kannada",
    "ta": "tamil",
    "te": "telugu",
    "mr": "marathi",
    "ml": "malayalam",
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pack-id", required=True)
    parser.add_argument("--limit", type=int)
    args = parser.parse_args()

    try:
        from datasets import load_dataset
    except ImportError as exc:
        raise SystemExit(
            "Install requirements-hf.txt first."
        ) from exc

    context = load_pack_context(
        PROJECT_ROOT,
        args.pack_id,
    )
    language_code = (
        context.pack.region_language_code
    )
    expected_language = (
        LANGUAGE_NAMES[language_code]
    )

    dataset = load_dataset(
        "NisargBhavsar25/koel-benchmark",
        split="koel_l",
    )

    city = context.pack.city.casefold()

    rows = []
    for row in dataset:
        if (
            str(
                row.get(
                    "language",
                    "",
                )
            ).casefold()
            != expected_language
        ):
            continue

        if (
            str(
                row.get(
                    "city",
                    "",
                )
            ).casefold()
            != city
        ):
            continue

        locality = str(
            row.get(
                "locality_name"
            )
            or ""
        ).strip()

        if not locality:
            continue

        rows.append(row)

        if (
            args.limit
            and len(rows) >= args.limit
        ):
            break

    profile = LanguageProfileRegistry(
        PROJECT_ROOT
        / "configs"
        / "language_profiles.json"
    ).get(language_code)

    output = (
        PROJECT_ROOT
        / "data"
        / "reference_sources"
        / "koel"
        / f"{args.pack_id}.csv"
    )
    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    fields = [
        "generation_id",
        "pack_id",
        "city",
        "language",
        "locality_name",
        "locality_looks_native",
        "generated_sentence",
        "upstream_dataset",
        "upstream_license",
    ]

    with output.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=fields,
        )
        writer.writeheader()

        for row in rows:
            locality = str(
                row.get(
                    "locality_name"
                )
                or ""
            )

            writer.writerow({
                "generation_id": (
                    row.get(
                        "generation_id",
                        "",
                    )
                ),
                "pack_id": (
                    args.pack_id
                ),
                "city": (
                    context.pack.city
                ),
                "language": (
                    context.pack.region_language
                ),
                "locality_name": (
                    locality
                ),
                "locality_looks_native": (
                    native_script_fraction(
                        locality,
                        profile,
                    )
                    >= 0.6
                ),
                "generated_sentence": (
                    row.get(
                        "generated_sentence",
                        "",
                    )
                ),
                "upstream_dataset": (
                    "NisargBhavsar25/koel-benchmark"
                ),
                "upstream_license": (
                    "Apache-2.0"
                ),
            })

    print(json.dumps({
        "pack_id": args.pack_id,
        "rows": len(rows),
        "output": str(
            output.relative_to(
                PROJECT_ROOT
            )
        ),
        "note": (
            "Reference-only import. "
            "It is not automatically promoted "
            "to reviewed MapVoice training data."
        ),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
