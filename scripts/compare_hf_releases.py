from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from mapvoice_llm.release_diff import write_release_diff


def resolve(path: str) -> Path:
    value = Path(path)
    return (
        value
        if value.is_absolute()
        else PROJECT_ROOT / value
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--first", required=True)
    parser.add_argument("--second", required=True)
    parser.add_argument(
        "--output",
        default=(
            "outputs/hf_datasets/"
            "release_diff.json"
        ),
    )
    args = parser.parse_args()

    result = write_release_diff(
        first_dir=resolve(args.first),
        second_dir=resolve(args.second),
        output=resolve(args.output),
    )

    print(json.dumps(
        result,
        ensure_ascii=False,
        indent=2,
    ))


if __name__ == "__main__":
    main()
