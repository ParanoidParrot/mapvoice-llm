from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from mapvoice_llm.publication_readiness import assess_release

parser = argparse.ArgumentParser()
parser.add_argument("--release-dir", required=True)
args = parser.parse_args()

path = Path(args.release_dir)
if not path.is_absolute():
    path = PROJECT_ROOT / path

print(json.dumps(
    assess_release(path),
    ensure_ascii=False,
    indent=2,
))
