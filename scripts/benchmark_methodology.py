from __future__ import annotations

import json
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from mapvoice_llm.benchmark_protocol import BenchmarkProtocol

protocol = BenchmarkProtocol.load(
    PROJECT_ROOT / "configs" / "benchmark_protocol.json"
)

print(json.dumps(protocol.to_dict(), indent=2))
