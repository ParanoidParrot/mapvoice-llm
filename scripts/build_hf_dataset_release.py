from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from mapvoice_llm.hf_dataset_release import build_hf_release

parser = argparse.ArgumentParser()
parser.add_argument("--name", default="mapvoice-india-toponyms-preview")
parser.add_argument("--version", default="0.1.0")
args = parser.parse_args()

print(json.dumps(
    build_hf_release(
        project_root=PROJECT_ROOT,
        release_name=args.name,
        version=args.version,
    ),
    ensure_ascii=False,
    indent=2,
))
