from __future__ import annotations

import json
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from mapvoice_llm.review_dashboard import review_progress

print(json.dumps(
    review_progress(PROJECT_ROOT),
    ensure_ascii=False,
    indent=2,
))
