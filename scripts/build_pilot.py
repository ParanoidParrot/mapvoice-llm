from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from mapvoice_llm.pack_context import load_pack_context
from mapvoice_llm.pilot_builder import build_pilot
from mapvoice_llm.pilot_profiles import PilotProfileRegistry


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pack-id", required=True)
    parser.add_argument("--seed", type=int, default=20261018)
    args = parser.parse_args()

    context = load_pack_context(
        PROJECT_ROOT,
        args.pack_id,
    )

    profile = PilotProfileRegistry(
        PROJECT_ROOT / "configs" / "pilot_profiles.json"
    ).get(args.pack_id)

    result = build_pilot(
        project_root=PROJECT_ROOT,
        pack=context.pack,
        profile=profile,
        seed=args.seed,
    )

    print(json.dumps(
        result,
        ensure_ascii=False,
        indent=2,
    ))


if __name__ == "__main__":
    main()
