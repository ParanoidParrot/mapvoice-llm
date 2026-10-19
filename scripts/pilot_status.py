from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from mapvoice_llm.pilot_builder import pilot_status
from mapvoice_llm.pilot_profiles import PilotProfileRegistry


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pack-id")
    parser.add_argument("--all", action="store_true")
    args = parser.parse_args()

    registry = PilotProfileRegistry(
        PROJECT_ROOT / "configs" / "pilot_profiles.json"
    )

    profiles = (
        registry.list()
        if args.all
        else [registry.get(args.pack_id)]
    )

    results = [
        pilot_status(
            project_root=PROJECT_ROOT,
            pack_id=profile.pack_id,
            profile=profile,
        )
        for profile in profiles
    ]

    print(json.dumps(
        {"pilots": results},
        ensure_ascii=False,
        indent=2,
    ))


if __name__ == "__main__":
    main()
