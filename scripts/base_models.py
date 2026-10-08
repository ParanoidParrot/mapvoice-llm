from __future__ import annotations

import json
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from mapvoice_llm.base_model_registry import BaseModelRegistry

registry = BaseModelRegistry(
    PROJECT_ROOT / "configs" / "base_models.json"
)
print(json.dumps({
    "reference": registry.reference().to_dict(),
    "models": [model.to_dict() for model in registry.list()],
}, indent=2))
