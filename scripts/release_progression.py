from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from mapvoice_llm.release_progression import assess_release_progression


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--release-dir",
        required=True,
    )
    args = parser.parse_args()

    release_dir = Path(
        args.release_dir
    )
    if not release_dir.is_absolute():
        release_dir = (
            PROJECT_ROOT
            / release_dir
        )

    print(json.dumps(
        assess_release_progression(
            project_root=PROJECT_ROOT,
            release_dir=release_dir,
        ),
        ensure_ascii=False,
        indent=2,
    ))


if __name__ == "__main__":
    main()
