from __future__ import annotations
import json
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from mapvoice_llm.source_registry import SourceRegistry

items = SourceRegistry(PROJECT_ROOT / "configs/source_registry.json").list()
print(json.dumps({"sources": [x.to_dict() for x in items]}, indent=2))
